import json
import logging
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.core.cache import cache

from .models import (
    UserProfile, Assessment, AssessmentQuestion,
    AssessmentAnswer, Recommendation, ContactMessage
)
from .services.assessment import generate_skill_questions, score_assessment
from .services.recommendations import generate_recommendation_plan
from .guardrails import sanitize_input, validate_input_guardrails, moderate_output

logger = logging.getLogger(__name__)


def check_rate_limit(request, max_calls=15, period=60) -> bool:
    """Basic rate limiting per user/IP on intensive LLM generation endpoints."""
    identifier = request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR', '127.0.0.1')
    cache_key = f"rate_limit_{identifier}"
    current = cache.get(cache_key, 0)
    if current >= max_calls:
        return False
    cache.set(cache_key, current + 1, period)
    return True


def get_or_create_user_profile(user):
    """Safely get or initialize UserProfile for user."""
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'target_role': 'Software Engineer',
            'weekly_hours': 10,
            'experience_level': 'beginner'
        }
    )
    return profile


def home(request):
    """Minimal SkillHer landing page."""
    active_assessment = None
    if request.user.is_authenticated:
        profile = get_or_create_user_profile(request.user)
        active_assessment = Assessment.objects.filter(user_profile=profile).order_by('-created_at').first()

    return render(request, 'recommender/home.html', {
        'active_assessment': active_assessment
    })


def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            get_or_create_user_profile(user)
            login(request, user)
            messages.success(request, "Welcome to SkillHer! Let's assess your first skill.")
            return redirect('skill_assessment')
    else:
        form = UserCreationForm()

    return render(request, 'recommender/register.html', {'form': form})


@login_required
def profile(request):
    """User profile management and skill level progression history."""
    user_profile = get_or_create_user_profile(request.user)

    if request.method == 'POST':
        target_role = sanitize_input(request.POST.get('target_role', ''))
        weekly_hours = request.POST.get('weekly_hours', '10')
        location = sanitize_input(request.POST.get('location', ''))

        try:
            user_profile.weekly_hours = max(1, min(80, int(weekly_hours)))
        except ValueError:
            user_profile.weekly_hours = 10

        user_profile.target_role = target_role[:100]
        user_profile.location = location[:100]
        user_profile.save()
        messages.success(request, "Your preferences have been saved.")
        return redirect('profile')

    assessments = Assessment.objects.filter(user_profile=user_profile).order_by('-created_at')
    # Pair with corresponding recommendation if available
    for a in assessments:
        a.recommendation = Recommendation.objects.filter(assessment=a).first()

    return render(request, 'recommender/profile.html', {
        'profile': user_profile,
        'assessments': assessments
    })


@login_required
def skill_assessment(request):
    """
    Dynamic adaptive skill assessment:
    Step 1: Enter skill (free text), goal, weekly hours.
    Step 2: Server generates 8-10 adaptive questions; rendered with 1-question progression.
    Step 3: Server-side scoring and automatic recommendation synthesis.
    """
    user_profile = get_or_create_user_profile(request.user)

    # Allow re-assessment pre-filling via query param
    initial_skill = request.GET.get('reassess', '').strip()

    if request.method == 'GET':
        step = request.GET.get('step', 'init')
        assessment_id = request.GET.get('assessment_id')

        if step == 'questions' and assessment_id:
            assessment = get_object_or_404(Assessment, id=assessment_id, user_profile=user_profile)
            questions = assessment.questions.all().order_by('order')
            return render(request, 'recommender/skill_assessment.html', {
                'step': 'questions',
                'assessment': assessment,
                'questions': questions
            })

        return render(request, 'recommender/skill_assessment.html', {
            'step': 'init',
            'initial_skill': initial_skill,
            'default_hours': user_profile.weekly_hours or 10
        })

    # POST Handling
    action = request.POST.get('action', 'start')

    if action == 'start':
        skill_name = sanitize_input(request.POST.get('skill_name', '')).strip()
        goal = sanitize_input(request.POST.get('goal', 'Career Growth')).strip()
        weekly_hours = request.POST.get('weekly_hours', '10')

        if not skill_name:
            messages.error(request, "Please enter a skill you want to learn or benchmark.")
            return redirect('skill_assessment')

        if not check_rate_limit(request):
            messages.error(request, "You have reached the temporary assessment generation limit. Please try again shortly.")
            return redirect('skill_assessment')

        try:
            hours = max(1, min(80, int(weekly_hours)))
        except ValueError:
            hours = 10

        user_profile.weekly_hours = hours
        user_profile.save()

        # Create assessment record
        assessment = Assessment.objects.create(
            user_profile=user_profile,
            skill_name=skill_name,
            goal=goal,
            weekly_hours=hours
        )

        # Generate questions via service
        generated_questions = generate_skill_questions(skill_name, goal)

        for q_dict in generated_questions:
            AssessmentQuestion.objects.create(
                assessment=assessment,
                order=q_dict.get('order', 1),
                question_type=q_dict.get('question_type', 'mcq'),
                topic=q_dict.get('topic', 'Core'),
                difficulty=q_dict.get('difficulty', 'intermediate'),
                question_text=q_dict.get('question_text', ''),
                option_a=q_dict.get('option_a', ''),
                option_b=q_dict.get('option_b', ''),
                option_c=q_dict.get('option_c', ''),
                option_d=q_dict.get('option_d', ''),
                correct_option=q_dict.get('correct_option', ''),
                explanation=q_dict.get('explanation', '')
            )

        return redirect(f"{request.path}?step=questions&assessment_id={assessment.id}")

    elif action == 'submit_answers':
        assessment_id = request.POST.get('assessment_id')
        assessment = get_object_or_404(Assessment, id=assessment_id, user_profile=user_profile)
        questions = assessment.questions.all().order_by('order')

        answers_payload = []
        for q in questions:
            user_ans = request.POST.get(f'q_{q.id}', '').strip()
            rating_val = None
            if q.question_type == 'rating':
                try:
                    rating_val = int(user_ans)
                except ValueError:
                    rating_val = 3

            answers_payload.append({
                'question': q,
                'answer': user_ans,
                'rating': rating_val
            })

            # Record answer in DB
            is_correct = False
            if q.question_type in ('mcq', 'scenario') and q.correct_option:
                is_correct = (user_ans.lower() == q.correct_option.lower())

            AssessmentAnswer.objects.update_or_create(
                assessment=assessment,
                question=q,
                defaults={
                    'selected_option': user_ans[:10],
                    'rating_value': rating_val,
                    'is_correct': is_correct
                }
            )

        # Server-side score
        result = score_assessment(answers_payload)
        assessment.score_percentage = result['score_percentage']
        assessment.level = result['level']
        assessment.strengths = result['strengths']
        assessment.gaps = result['gaps']
        assessment.summary = result['summary']
        assessment.completed = True
        assessment.save()

        # Synthesize recommendation roadmap
        plan = generate_recommendation_plan(
            skill=assessment.skill_name,
            level=assessment.level,
            weekly_hours=assessment.weekly_hours,
            goal=assessment.goal,
            location=user_profile.location
        )

        rec = Recommendation.objects.create(
            user_profile=user_profile,
            assessment=assessment,
            recommendation_type='realtime_roadmap',
            title=f"{assessment.skill_name} Learning Roadmap",
            skill_name=assessment.skill_name,
            weekly_hours=assessment.weekly_hours,
            description=plan.get('gap_summary', ''),
            match_score=assessment.score_percentage,
            roadmap_data=plan.get('roadmap', []),
            project_ideas=plan.get('projects', []),
            resume_tips=plan.get('resume_tips', []),
            interview_topics=plan.get('interview_topics', []),
            resources_data=plan.get('resources_data', {}),
            completed_milestones=[]
        )

        messages.success(request, f"Assessment complete! Your personalized roadmap for {assessment.skill_name} is ready.")
        return redirect('recommendation_detail', rec_id=rec.id)

    return redirect('skill_assessment')


@login_required
def view_recommendations(request):
    """View active learning plans and assessment history."""
    user_profile = get_or_create_user_profile(request.user)
    recommendations = Recommendation.objects.filter(user_profile=user_profile).order_by('-created_at')

    if not recommendations.exists():
        messages.info(request, "You haven't generated any learning roadmaps yet. Start an assessment!")
        return redirect('skill_assessment')

    return render(request, 'recommender/recommendations.html', {
        'recommendations': recommendations,
        'latest_rec': recommendations.first()
    })


@login_required
def recommendation_detail(request, rec_id):
    """
    Detailed printable view of a personalized roadmap:
    Gap analysis, week-by-week milestones with checkboxes, project ideas,
    deterministic resources (YouTube, GitHub, Internships, Docs, Communities),
    and resume/interview advice.
    """
    user_profile = get_or_create_user_profile(request.user)
    rec = get_object_or_404(Recommendation, id=rec_id, user_profile=user_profile)

    # Calculate completed percentage
    completed_milestones = set(rec.completed_milestones or [])
    total_items = 0
    done_items = 0

    weeks = rec.roadmap_data if isinstance(rec.roadmap_data, list) else []
    for week in weeks:
        items = week.get('items', [])
        for idx, item in enumerate(items):
            item_key = f"w{week.get('week_number')}_i{idx}"
            is_done = item_key in completed_milestones
            if is_done:
                done_items += 1
            total_items += 1

    progress_pct = round((done_items / total_items * 100)) if total_items > 0 else 0

    return render(request, 'recommender/recommendation_detail.html', {
        'recommendation': rec,
        'assessment': rec.assessment,
        'weeks': weeks,
        'completed_milestones': completed_milestones,
        'progress_pct': progress_pct,
        'resources': rec.resources_data or {},
        'projects': rec.project_ideas or [],
        'resume_tips': rec.resume_tips or [],
        'interview_topics': rec.interview_topics or []
    })


@login_required
@require_POST
def api_toggle_milestone(request):
    """AJAX endpoint to toggle milestone checkbox and persist progress."""
    try:
        data = json.loads(request.body)
        rec_id = data.get('recommendation_id')
        milestone_key = data.get('milestone_key')
        completed = data.get('completed', False)

        user_profile = get_or_create_user_profile(request.user)
        rec = get_object_or_404(Recommendation, id=rec_id, user_profile=user_profile)

        current_milestones = set(rec.completed_milestones or [])
        if completed:
            current_milestones.add(milestone_key)
        else:
            current_milestones.discard(milestone_key)

        rec.completed_milestones = list(current_milestones)
        rec.save(update_fields=['completed_milestones'])

        return JsonResponse({'status': 'success', 'completed_count': len(current_milestones)})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def resources(request):
    """Curated open documentation and community links for women in technology."""
    return render(request, 'recommender/resources.html')


def about(request):
    """About SkillHer mission and platform."""
    return render(request, 'recommender/about.html')


def logout_view(request):
    """Log out user and render confirmation."""
    auth_logout(request)
    return render(request, 'recommender/logout.html')


def send_email_via_python_smtp(payload: dict) -> tuple[bool, dict]:
    """Pure Python TLS smtplib email dispatcher with error handling."""
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_pass = os.getenv('SMTP_PASS', '').replace(' ', '')
    contact_email = os.getenv('CONTACT_EMAIL', 'malthumkarvarun@gmail.com')

    if not smtp_user or not smtp_pass:
        return False, {'error': 'SMTP credentials not configured'}

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = contact_email
        msg['Subject'] = f"[SkillHer Contact] {payload.get('subject', 'Inquiry')}"
        body = f"""Name: {payload.get('name')}
Email: {payload.get('email')}
Category: {payload.get('category')}

Message:
{payload.get('message')}
"""
        msg.attach(MIMEText(body, 'plain'))
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls(context=context)
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True, {'message': 'Sent via smtplib'}
    except Exception as e:
        logger.error(f"Failed to dispatch email via smtplib: {e}")
        return False, {'error': str(e)}


def contact(request):
    """Contact form with database logging and email dispatch."""
    if request.method == 'POST':
        name = sanitize_input(request.POST.get('name', ''))
        email = sanitize_input(request.POST.get('email', ''))
        category = sanitize_input(request.POST.get('category', 'general'))
        subject = sanitize_input(request.POST.get('subject', ''))
        message_text = sanitize_input(request.POST.get('message', ''))

        if not name or not email or not message_text:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'recommender/contact.html')

        # Persist to database
        ContactMessage.objects.create(
            name=name,
            email=email,
            category=category,
            subject=subject,
            message=message_text,
            sent_via_nodemailer=False
        )

        # Attempt sending
        send_email_via_python_smtp({
            'name': name,
            'email': email,
            'category': category,
            'subject': subject,
            'message': message_text
        })

        messages.success(request, "Thank you! Your message has been received and our team will get back to you shortly.")
        return redirect('contact')

    return render(request, 'recommender/contact.html')


@require_POST
def api_contact(request):
    """AJAX JSON endpoint for contact form."""
    try:
        data = json.loads(request.body)
        name = sanitize_input(data.get('name', ''))
        email = sanitize_input(data.get('email', ''))
        category = sanitize_input(data.get('category', 'general'))
        subject = sanitize_input(data.get('subject', ''))
        message_text = sanitize_input(data.get('message', ''))

        msg = ContactMessage.objects.create(
            name=name,
            email=email,
            category=category,
            subject=subject,
            message=message_text,
            sent_via_nodemailer=False,
            nodemailer_message_id='<python-smtp-sent>'
        )
        return JsonResponse({'status': 'success', 'messageId': msg.nodemailer_message_id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# Lightweight advisor endpoint preserving backwards compatibility
@require_POST
def api_chatbot(request):
    """Contextual AI advice endpoint with guardrail defense."""
    try:
        data = json.loads(request.body)
        raw_msg = data.get('message', '')
        flagged, reason, clean_text = validate_input_guardrails(raw_msg)
        if flagged:
            return JsonResponse({
                'status': 'success',
                'guardrail_flagged': True,
                'guardrail_reason': reason,
                'reply': "Hello! I am Aria, your SkillHer mentor. Let's focus on your career roadmap, interview preparation, and technical learning goals."
            })

        reply = f"That is a great direction for your career roadmap in {clean_text[:40]}. Focusing on deliberate weekly milestones will help you build solid confidence."
        return JsonResponse({'status': 'success', 'reply': moderate_output(reply)})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)