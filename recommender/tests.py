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
        # 1. YouTube link encoding (explicitly test fallback search URL encoding for special characters)
        with patch('django.conf.settings.YOUTUBE_API_KEY', ''):
            yt_fallback = build_youtube_links('Data Structures & Algorithms')
            self.assertTrue(len(yt_fallback) >= 1)
            self.assertIn('https://www.youtube.com/results?search_query=Data+Structures+%26+Algorithms', yt_fallback[0]['url'])

            cpp_fallback = build_youtube_links('C++')
            self.assertIn('search_query=C%2B%2B', cpp_fallback[0]['url'])

            csharp_fallback = build_youtube_links('C#')
            self.assertIn('search_query=C%23', csharp_fallback[0]['url'])

        # 2. GitHub (API may return live repo or fallback search URL, both valid)
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
        self.assertTrue('Search YouTube' in content or 'Video Tutorials' in content)

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


class QuestionCachingTestCase(TestCase):
    """Test 7-day database question set caching behavior."""

    @patch('recommender.services.assessment.query_groq')
    def test_database_caching_and_reuse_within_7_days(self, mock_groq):
        from datetime import timedelta
        from django.utils import timezone
        from recommender.models import AssessmentQuestionCache

        mock_groq.return_value = {
            'skill': 'Django',
            'questions': [
                {
                    'order': i,
                    'question_type': 'mcq' if i <= 4 else 'rating',
                    'topic': 'ORM',
                    'difficulty': 'beginner',
                    'question_text': f'Django Question {i}?',
                    'option_a': 'Opt A',
                    'option_b': 'Opt B',
                    'option_c': 'Opt C',
                    'option_d': 'Opt D',
                    'correct_option': 'a' if i <= 4 else '',
                    'explanation': 'Explanation'
                }
                for i in range(1, 8)
            ]
        }

        # 1. First call: Cache miss -> calls Groq
        q_set_1 = generate_skill_questions("Django", "Backend Dev")
        self.assertEqual(mock_groq.call_count, 1)
        self.assertEqual(len(q_set_1), 7)

        # Verify entry created in DB with normalized fields
        cache_entry = AssessmentQuestionCache.objects.filter(
            normalized_skill='django',
            normalized_goal='backend dev'
        ).first()
        self.assertIsNotNone(cache_entry)
        self.assertEqual(len(cache_entry.questions_data), 7)

        # 2. Second call with case differences: Cache HIT -> does NOT call Groq again
        q_set_2 = generate_skill_questions("  DJANGO  ", "  backend dev  ")
        self.assertEqual(mock_groq.call_count, 1)  # Groq call count remains 1!
        self.assertEqual(len(q_set_2), 7)
        self.assertEqual(q_set_1[0]['question_text'], q_set_2[0]['question_text'])

        # 3. Simulate cache expiration (>7 days ago)
        cache_entry.created_at = timezone.now() - timedelta(days=8)
        cache_entry.save()

        # Third call: Cache expired -> calls Groq again
        q_set_3 = generate_skill_questions("Django", "Backend Dev")
        self.assertEqual(mock_groq.call_count, 2)


class UrlTrailingSlashRedirectTestCase(TestCase):
    """Test APPEND_SLASH redirection for clean URL handling."""
    def setUp(self):
        self.client = Client()

    def test_trailing_slash_redirects(self):
        for route in ('contact', 'about', 'login'):
            res = self.client.get(f'/{route}')
            self.assertEqual(res.status_code, 301, f"GET /{route} must return 301 redirect")
            self.assertEqual(res.url, f'/{route}/')

            # Follow redirect and verify 200 OK
            follow_res = self.client.get(f'/{route}', follow=True)
            self.assertEqual(follow_res.status_code, 200)


class MarkdownRendererTestCase(TestCase):
    """Test safe zero-dependency Markdown-to-HTML converter."""

    def test_headings_conversion(self):
        from recommender.services.markdown_render import render_markdown
        text = "# Heading 1\n## Heading 2\n### Heading 3\n#### Heading 4"
        out = render_markdown(text)
        self.assertIn('<h1>Heading 1</h1>', out)
        self.assertIn('<h2>Heading 2</h2>', out)
        self.assertIn('<h3>Heading 3</h3>', out)
        self.assertIn('<h4>Heading 4</h4>', out)

    def test_bold_italic_and_inline_code(self):
        from recommender.services.markdown_render import render_markdown
        text = "This is **bold** text, *italic* word, and `my_code()` function."
        out = render_markdown(text)
        self.assertIn('<strong>bold</strong>', out)
        self.assertIn('<em>italic</em>', out)
        self.assertIn('<code>my_code()</code>', out)

    def test_lists_unordered_and_ordered(self):
        from recommender.services.markdown_render import render_markdown
        ul_text = "- Item A\n* Item B\n+ Item C"
        ul_out = render_markdown(ul_text)
        self.assertIn('<ul>', ul_out)
        self.assertIn('<li>Item A</li>', ul_out)
        self.assertIn('<li>Item B</li>', ul_out)
        self.assertIn('<li>Item C</li>', ul_out)
        self.assertIn('</ul>', ul_out)

        ol_text = "1. Step One\n2. Step Two"
        ol_out = render_markdown(ol_text)
        self.assertIn('<ol>', ol_out)
        self.assertIn('<li>Step One</li>', ol_out)
        self.assertIn('<li>Step Two</li>', ol_out)
        self.assertIn('</ol>', ol_out)

    def test_links_safe_vs_malicious(self):
        from recommender.services.markdown_render import render_markdown
        safe_text = "Visit [Official Website](https://skillher.org) for details."
        safe_out = render_markdown(safe_text)
        self.assertIn('<a href="https://skillher.org" target="_blank" rel="noopener noreferrer">Official Website</a>', safe_out)

        # Malicious links must be neutralized
        bad_text = "Click [Exploit](javascript:alert(1)) or [Data](data:text/html;base64,...)"
        bad_out = render_markdown(bad_text)
        self.assertNotIn('<a href="javascript:', bad_out)
        self.assertNotIn('<a href="data:', bad_out)
        self.assertIn('Exploit (javascript:alert(1))', bad_out)

    def test_code_blocks(self):
        from recommender.services.markdown_render import render_markdown
        code = "```python\ndef solve():\n    return 42\n```"
        out = render_markdown(code)
        self.assertIn('<pre><code>def solve():\n    return 42</code></pre>', out)

    def test_xss_neutralization(self):
        from recommender.services.markdown_render import render_markdown
        dirty = "<script>alert('xss')</script> and <img src=x onerror=alert(1)>"
        out = render_markdown(dirty)
        self.assertNotIn('<script>', out)
        self.assertNotIn('<img', out)
        self.assertIn('&lt;script&gt;', out)
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;', out)

    def test_single_line_legacy_record_repair(self):
        from recommender.services.markdown_render import render_markdown
        legacy = "Baseline summary. ### Key Milestones: * Setup environment * Build API"
        out = render_markdown(legacy)
        self.assertIn('<h3>Key Milestones:</h3>', out)
        self.assertIn('<ul>', out)
        self.assertIn('<li>Setup environment</li>', out)
        self.assertIn('<li>Build API</li>', out)

    def test_model_name_stripped(self):
        from recommender.services.markdown_render import render_markdown
        text = "### Strategic AI Career Guidance (qwen/qwen3.8-27b):\nRoadmap overview."
        out = render_markdown(text)
        self.assertNotIn('Strategic AI Career Guidance', out)
        self.assertNotIn('qwen', out)
        self.assertIn('<p>Roadmap overview.</p>', out)


