import json
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders

from recommender.models import (
    UserProfile, Assessment, AssessmentQuestion,
    Recommendation, ContactMessage
)
from recommender.services.assessment import (
    validate_question_schema,
    build_generic_fallback_questions,
    score_assessment,
    generate_skill_questions
)
from recommender.services.recommendations import (
    validate_roadmap_schema,
    generate_curated_fallback_roadmap,
    generate_recommendation_plan
)
from recommender.services.links import (
    build_youtube_links,
    build_github_links,
    build_internship_links,
    build_course_and_doc_links,
    build_community_and_cert_links
)


class TemplateAndStaticAssetsTestCase(TestCase):
    """Verify SkillHer branding, SVG assets, and base template rendering."""
    def setUp(self):
        self.client = Client()

    def test_static_logo_and_icon_exist_on_filesystem(self):
        icon_path = finders.find('img/skillher-icon.svg')
        logo_path = finders.find('img/skillher-logo.svg')
        css_path = finders.find('css/app.css')
        js_path = finders.find('js/app.js')

        self.assertIsNotNone(icon_path, "static/img/skillher-icon.svg must resolve via static finders")
        self.assertIsNotNone(logo_path, "static/img/skillher-logo.svg must resolve via static finders")
        self.assertIsNotNone(css_path, "static/css/app.css must resolve via static finders")
        self.assertIsNotNone(js_path, "static/js/app.js must resolve via static finders")

    def test_base_template_renders_branding(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check favicon and logo references
        self.assertIn('skillher-icon.svg', content)
        self.assertIn('skillher-logo.svg', content)
        self.assertIn('app.css', content)
        # Check brand name and footer tagline
        self.assertIn('SkillHer', content)
        self.assertIn('Learn the skill. Land the opportunity.', content)

    def test_login_and_register_pages_render_48px_logo(self):
        login_res = self.client.get(reverse('login'))
        self.assertEqual(login_res.status_code, 200)
        self.assertIn('height="48"', login_res.content.decode('utf-8'))

        reg_res = self.client.get(reverse('register'))
        self.assertEqual(reg_res.status_code, 200)
        self.assertIn('height="48"', reg_res.content.decode('utf-8'))


class ServiceLogicTestCase(TestCase):
    """Test schema validation, scoring engine, and deterministic link generators."""

    def test_assessment_schema_validation_and_fallback(self):
        # Valid schema
        valid_data = {
            'skill': 'React',
            'questions': [
                {
                    'order': i,
                    'question_type': 'mcq' if i <= 4 else 'rating',
                    'topic': 'Components',
                    'difficulty': 'beginner',
                    'question_text': f'Sample question {i}?',
                    'option_a': 'Option A',
                    'option_b': 'Option B',
                    'option_c': 'Option C',
                    'option_d': 'Option D',
                    'correct_option': 'a' if i <= 4 else '',
                    'explanation': 'Explanation'
                }
                for i in range(1, 8)
            ]
        }
        self.assertTrue(validate_question_schema(valid_data))

        # Invalid schema (missing required fields / too few questions)
        invalid_data = {'skill': 'React', 'questions': [{'question_text': 'short'}]}
        self.assertFalse(validate_question_schema(invalid_data))

        # Fallback question builder generates valid structure
        fallback = build_generic_fallback_questions('Rust')
        self.assertTrue(len(fallback) >= 6)
        self.assertEqual(fallback[0]['question_type'], 'mcq')

    def test_roadmap_schema_validation(self):
        valid_roadmap = {
            'gap_summary': 'Demonstrates basic syntax understanding with gaps in async flows.',
            'roadmap': [
                {'week_number': 1, 'title': 'Week 1', 'concrete_outcome': 'Build working app'},
                {'week_number': 2, 'title': 'Week 2', 'concrete_outcome': 'Connect database'},
                {'week_number': 3, 'title': 'Week 3', 'concrete_outcome': 'Deploy service'}
            ]
        }
        self.assertTrue(validate_roadmap_schema(valid_roadmap))

        invalid_roadmap = {'gap_summary': '', 'roadmap': []}
        self.assertFalse(validate_roadmap_schema(invalid_roadmap))

    def test_scoring_engine_objective_and_rating(self):
        # Setup questions and answers
        questions_payload = [
            {
                'question': {'topic': 'Syntax', 'question_type': 'mcq', 'correct_option': 'b'},
                'answer': 'b',  # Correct: earned 2.0 / 2.0
                'rating': None
            },
            {
                'question': {'topic': 'Syntax', 'question_type': 'mcq', 'correct_option': 'c'},
                'answer': 'a',  # Incorrect: earned 0.0 / 2.0
                'rating': None
            },
            {
                'question': {'topic': 'Testing', 'question_type': 'rating', 'correct_option': ''},
                'answer': '',
                'rating': 4  # 4 on 1-5 scale: earned 0.8 / 1.0
            }
        ]

        scored = score_assessment(questions_payload)
        self.assertIn('score_percentage', scored)
        self.assertIn('level', scored)
        self.assertIn('strengths', scored)
        self.assertIn('gaps', scored)
        # Total possible: 2 + 2 + 1 = 5. Earned: 2 + 0 + 0.8 = 2.8 -> 56% -> Intermediate
        self.assertEqual(scored['level'], 'Intermediate')
        self.assertAlmostEqual(scored['score_percentage'], 56.0, delta=0.5)

    def test_link_builders_url_encoding_and_integrity(self):
        # 1. YouTube
        yt_links = build_youtube_links('Data Structures & Algorithms')
        self.assertTrue(len(yt_links) >= 1)
        self.assertIn('https://www.youtube.com/results?search_query=Data+Structures+%26+Algorithms', yt_links[0]['url'])

        # 2. GitHub (API may return live repo like https://github.com/vercel/next.js or search URL)
        gh_links = build_github_links('Next.js')
        self.assertTrue(len(gh_links) >= 1)
        self.assertIn('github.com', gh_links[0]['url'])

        # 3. Internships
        internships = build_internship_links('Machine Learning', location='New York')
        self.assertEqual(len(internships), 4)
        linkedin = next(item for item in internships if item['portal'] == 'LinkedIn Jobs')
        self.assertIn('Machine+Learning+intern', linkedin['url'])
        self.assertIn('New+York', linkedin['url'])

        # 4. Courses & Docs
        docs = build_course_and_doc_links('python')
        self.assertTrue(any('docs.python.org' in item['url'] for item in docs))
        self.assertTrue(any('freecodecamp.org' in item['url'] for item in docs))


class AssessmentAndRoadmapViewsTestCase(TestCase):
    """End-to-end view tests with mocked Groq LLM integration."""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='sarah_dev', password='password123', email='sarah@example.com')
        self.profile = UserProfile.objects.create(user=self.user, target_role='Data Analyst', weekly_hours=10)
        self.client.login(username='sarah_dev', password='password123')

    @patch('recommender.services.assessment.query_groq')
    @patch('recommender.services.recommendations.query_groq')
    def test_happy_path_assessment_to_roadmap(self, mock_rec_groq, mock_assess_groq):
        # Mock Assessment LLM response (requires >= 6 questions for schema validation)
        mock_assess_groq.return_value = {
            'skill': 'Data Analysis',
            'questions': [
                {
                    'order': 1,
                    'question_type': 'mcq',
                    'topic': 'Pandas',
                    'difficulty': 'beginner',
                    'question_text': 'What method loads a CSV in Pandas?',
                    'option_a': 'pd.read_csv()',
                    'option_b': 'pd.load_csv()',
                    'option_c': 'pd.csv_open()',
                    'option_d': 'pd.import()',
                    'correct_option': 'a',
                    'explanation': 'read_csv is standard.'
                },
                {
                    'order': 2,
                    'question_type': 'mcq',
                    'topic': 'Data Cleaning',
                    'difficulty': 'beginner',
                    'question_text': 'How do you drop missing values in Pandas?',
                    'option_a': 'df.dropna()',
                    'option_b': 'df.remove_empty()',
                    'option_c': 'df.clean()',
                    'option_d': 'df.drop_none()',
                    'correct_option': 'a',
                    'explanation': 'dropna drops nulls.'
                },
                {
                    'order': 3,
                    'question_type': 'mcq',
                    'topic': 'Aggregation',
                    'difficulty': 'intermediate',
                    'question_text': 'Which method groups rows by key?',
                    'option_a': 'df.groupby()',
                    'option_b': 'df.aggregate_by()',
                    'option_c': 'df.cluster()',
                    'option_d': 'df.split()',
                    'correct_option': 'a',
                    'explanation': 'groupby groups rows.'
                },
                {
                    'order': 4,
                    'question_type': 'mcq',
                    'topic': 'SQL',
                    'difficulty': 'intermediate',
                    'question_text': 'Which clause filters grouped records?',
                    'option_a': 'HAVING',
                    'option_b': 'WHERE',
                    'option_c': 'LIMIT',
                    'option_d': 'FILTER',
                    'correct_option': 'a',
                    'explanation': 'HAVING filters aggregate groups.'
                },
                {
                    'order': 5,
                    'question_type': 'scenario',
                    'topic': 'Data Pipelines',
                    'difficulty': 'advanced',
                    'question_text': 'When scaling past memory limits, what should you use?',
                    'option_a': 'Chunked parsing or Polars/Dask',
                    'option_b': 'Single Python loop',
                    'option_c': 'Global variables',
                    'option_d': 'JSON serialization',
                    'correct_option': 'a',
                    'explanation': 'Chunking streams memory.'
                },
                {
                    'order': 6,
                    'question_type': 'rating',
                    'topic': 'Data Visualization',
                    'difficulty': 'self-assessment',
                    'question_text': 'Rate your comfort building charts.',
                    'option_a': '1 - Novice',
                    'option_b': '2 - Beginner',
                    'option_c': '3 - Competent',
                    'option_d': '4 - Expert',
                    'correct_option': '',
                    'explanation': 'Rating'
                }
            ]
        }

        # Step 1: Start assessment POST
        start_res = self.client.post(reverse('skill_assessment'), {
            'action': 'start',
            'skill_name': 'Data Analysis',
            'goal': 'First Tech Job / Internship',
            'weekly_hours': '12'
        }, follow=True)
        self.assertEqual(start_res.status_code, 200)

        assessment = Assessment.objects.filter(user_profile__user=self.user, skill_name='Data Analysis').first()
        self.assertIsNotNone(assessment)
        questions = assessment.questions.all()
        self.assertTrue(questions.count() >= 2)

        # Mock Roadmap LLM response (requires >= 3 weeks for schema validation)
        mock_rec_groq.return_value = {
            'gap_summary': 'Strong comprehension of tabular data operations with room for growth in dashboarding.',
            'roadmap': [
                {
                    'week_number': 1,
                    'title': 'Week 1: Exploratory Data Analysis with Pandas',
                    'topic': 'Pandas Data Analysis',
                    'concrete_outcome': 'Clean and summarize real dataset',
                    'items': ['Filter rows and columns', 'Handle null values with imputation']
                },
                {
                    'week_number': 2,
                    'title': 'Week 2: Relational Queries with SQL',
                    'topic': 'SQL Queries',
                    'concrete_outcome': 'Write complex JOINs',
                    'items': ['Aggregations', 'Window functions']
                },
                {
                    'week_number': 3,
                    'title': 'Week 3: Interactive Dashboards',
                    'topic': 'Data Visualization Dashboards',
                    'concrete_outcome': 'Deploy interactive visualization',
                    'items': ['Plotting KPIs', 'User filters']
                },
                {
                    'week_number': 4,
                    'title': 'Week 4: Portfolio Presentation',
                    'topic': 'Data Analysis Portfolio',
                    'concrete_outcome': 'Publish case study',
                    'items': ['Write README', 'Record walkthrough']
                }
            ],
            'projects': [
                {
                    'title': 'E-Commerce Analytics Pipeline',
                    'difficulty': 'Intermediate',
                    'description': 'End-to-end data pipeline parsing user sessions.',
                    'portfolio_highlight': 'Proves business KPI analysis skills.'
                }
            ],
            'resume_tips': ['Feature GitHub repo with EDA notebook.'],
            'interview_topics': ['Window functions and group-by aggregations.']
        }

        # Step 2: Submit answers POST
        q1 = questions.filter(question_type='mcq').first()
        q2 = questions.filter(question_type='rating').first()

        submit_payload = {
            'action': 'submit_answers',
            'assessment_id': assessment.id,
            f'q_{q1.id}': 'a',
            f'q_{q2.id}': '4'
        }

        submit_res = self.client.post(reverse('skill_assessment'), submit_payload, follow=True)
        self.assertEqual(submit_res.status_code, 200)

        # Verify assessment was updated and recommendation was generated
        assessment.refresh_from_db()
        self.assertTrue(assessment.completed)
        self.assertGreater(assessment.score_percentage, 0)

        rec = Recommendation.objects.filter(assessment=assessment).first()
        self.assertIsNotNone(rec)
        self.assertEqual(rec.skill_name, 'Data Analysis')

        # Verify recommendation detail page renders correctly
        detail_res = self.client.get(reverse('recommendation_detail', kwargs={'rec_id': rec.id}))
        self.assertEqual(detail_res.status_code, 200)
        content = detail_res.content.decode('utf-8')
        self.assertIn('Data Analysis Learning Roadmap', content)
        self.assertIn('Exploratory Data Analysis', content)
        self.assertIn('E-Commerce Analytics Pipeline', content)
        self.assertIn('Search YouTube', content)

    def test_milestone_toggle_api(self):
        rec = Recommendation.objects.create(
            user_profile=self.profile,
            title='Test Roadmap',
            skill_name='Testing',
            weekly_hours=10,
            roadmap_data=[{'week_number': 1, 'items': ['Item 1', 'Item 2']}],
            completed_milestones=[]
        )

        toggle_payload = {
            'recommendation_id': rec.id,
            'milestone_key': 'w1_i0',
            'completed': True
        }

        res = self.client.post(
            reverse('api_toggle_milestone'),
            data=json.dumps(toggle_payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        rec.refresh_from_db()
        self.assertIn('w1_i0', rec.completed_milestones)


class ContactAndPublicPagesTestCase(TestCase):
    """Test contact submission, email logging, and public pages."""
    def setUp(self):
        self.client = Client()

    def test_public_pages_load(self):
        for route in ('home', 'about', 'contact'):
            response = self.client.get(reverse(route))
            self.assertEqual(response.status_code, 200, f"Route {route} must load with 200")

    def test_contact_form_saves_to_database(self):
        data = {
            'name': 'Priya Sharma',
            'email': 'priya@example.com',
            'category': 'mentorship',
            'subject': 'Mentorship Programs',
            'message': 'Interested in contributing to SkillHer community.'
        }
        res = self.client.post(reverse('contact'), data, follow=True)
        self.assertEqual(res.status_code, 200)
        msg = ContactMessage.objects.filter(email='priya@example.com').first()
        self.assertIsNotNone(msg)
        self.assertEqual(msg.name, 'Priya Sharma')
