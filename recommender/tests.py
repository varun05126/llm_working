import json
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from recommender.models import ContactMessage
from recommender.views import send_email_via_nodemailer, send_email_via_python_smtp


class CorePagesTestCase(TestCase):
    """Test standard public routes load with HTTP 200"""
    def setUp(self):
        self.client = Client()

    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_about_page_loads(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_contact_page_loads(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contact Us')
        self.assertContains(response, 'malthumkarvarun@gmail.com')

    def test_resources_page_requires_login_and_loads(self):
        # Unauthenticated redirects to login
        response = self.client.get(reverse('resources'))
        self.assertEqual(response.status_code, 302)
        
        # Authenticated loads successfully
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='teststudent', password='testpassword123')
        self.client.login(username='teststudent', password='testpassword123')
        auth_response = self.client.get(reverse('resources'))
        self.assertEqual(auth_response.status_code, 200)


class ContactAndMailerTestCase(TestCase):
    """Test contact form submissions and dual-engine email dispatching"""
    def setUp(self):
        self.client = Client()

    @patch('recommender.views.send_email_via_nodemailer')
    def test_contact_form_post_success(self, mock_send):
        mock_send.return_value = (True, {'messageId': '<test-id@skillher>'})
        
        data = {
            'name': 'Test Submitter',
            'email': 'tester@example.com',
            'category': 'technical',
            'subject': 'Inquiry Test',
            'message': 'Hello from automated unit test suite.'
        }
        response = self.client.post(reverse('contact'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify database record
        msg = ContactMessage.objects.filter(email='tester@example.com').first()
        self.assertIsNotNone(msg)
        self.assertEqual(msg.name, 'Test Submitter')
        self.assertTrue(msg.sent_via_nodemailer)
        self.assertEqual(msg.nodemailer_message_id, '<test-id@skillher>')

    @patch('recommender.views.send_email_via_nodemailer')
    def test_api_contact_json_endpoint(self, mock_send):
        mock_send.return_value = (True, {'messageId': '<api-id@skillher>', 'engine': 'python_smtp'})
        
        payload = {
            'name': 'API Tester',
            'email': 'api@example.com',
            'category': 'general',
            'subject': 'API Subject',
            'message': 'API Message Test'
        }
        response = self.client.post(
            reverse('api_contact'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(res_json.get('status'), 'success')
        self.assertEqual(res_json.get('messageId'), '<api-id@skillher>')

    def test_python_smtp_missing_credentials_graceful_handling(self):
        # When SMTP_USER / SMTP_PASS are not configured, send_email_via_python_smtp returns False gracefully
        with patch.dict('os.environ', {'SMTP_USER': '', 'SMTP_PASS': ''}, clear=True):
            ok, info = send_email_via_python_smtp({
                'name': 'Graceful',
                'email': 'test@example.com',
                'category': 'General',
                'subject': 'Test',
                'message': 'Test'
            })
            self.assertFalse(ok)
            self.assertIn('SMTP credentials not configured', info.get('error', ''))

    def test_api_chatbot_returns_reply(self):
        payload = {'message': 'How do I start Month 1 in Docker?'}
        response = self.client.post(
            reverse('api_chatbot'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(res_json.get('status'), 'success')
        self.assertTrue(len(res_json.get('reply', '')) > 10)

    def test_realtime_recommendations_with_desired_skills(self):
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='skilllearner', password='password123')
        self.client.login(username='skilllearner', password='password123')
        
        payload = {
            'domain': 'web_dev',
            'target_role': 'Full-Stack Lead',
            'weekly_hours': 15,
            'desired_skills': 'Docker, GraphQL, Kubernetes'
        }
        response = self.client.post(
            reverse('api_realtime_recommendations'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(res_json.get('status'), 'success')
        self.assertEqual(res_json.get('desired_skills'), 'Docker, GraphQL, Kubernetes')
        # Check that requested skills are present in skills payload
        skill_names = [s['name'].lower() for s in res_json.get('skills', [])]
        self.assertTrue('docker' in skill_names or 'graphql' in skill_names or 'kubernetes' in skill_names)


