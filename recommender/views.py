import json
import os
import subprocess
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.db.models import Avg, Count, Q

from .models import (
    UserProfile, Skill, UserSkill, AssessmentQuestion,
    AssessmentResult, LearningResource, Recommendation,
    RecommendationSkill, RecommendationResource, ContactMessage
)


# ==============================================================================
# DOMAIN ROADMAP TEMPLATES & BENCHMARKS (For Real-Time Instant Synthesis)
# ==============================================================================
DOMAIN_BENCHMARKS = {
    'web_dev': {
        'title': 'Full-Stack Web Development Path',
        'target_roles': ['Full-Stack Developer', 'Frontend Engineer', 'Backend Engineer'],
        'core_skills': ['HTML & CSS', 'JavaScript & TypeScript', 'React', 'Python & Django', 'SQL & PostgreSQL', 'Git & GitHub'],
        'month_1': 'Foundations: Master semantic modern HTML/CSS, core JS/ES6+, and version control with Git.',
        'month_2': 'Application Layer: Build full-stack apps with React, Django REST framework, and PostgreSQL.',
        'month_3': 'Production & Scale: Deploy on cloud services, CI/CD workflows, web security, and system architecture.'
    },
    'ai_ml': {
        'title': 'AI & Machine Learning Specialist Track',
        'target_roles': ['AI/ML Engineer', 'Machine Learning Scientist', 'NLP Engineer'],
        'core_skills': ['Python for AI', 'Linear Algebra & Calculus', 'Data Analysis with Pandas', 'PyTorch / TensorFlow', 'Transformer Models & LLMs', 'MLOps & Deployment'],
        'month_1': 'Foundations: Mathematical principles, Python numerical libraries (NumPy, Pandas), and exploratory data analysis.',
        'month_2': 'Deep Learning: Train neural networks, computer vision, and fine-tuning transformer architectures.',
        'month_3': 'Production ML: MLOps pipelines, model quantization, serving endpoints, and ethical AI evaluation.'
    },
    'data_science': {
        'title': 'Data Science & Business Intelligence Track',
        'target_roles': ['Data Scientist', 'Data Analyst', 'BI Solutions Architect'],
        'core_skills': ['SQL Analytics', 'Python & Pandas', 'Statistical Modeling', 'Tableau & Data Viz', 'Machine Learning Basics', 'Experimentation & A/B Testing'],
        'month_1': 'Data Wrangling: SQL window functions, exploratory data analysis, and statistical hypothesis testing.',
        'month_2': 'Predictive Modeling: Supervised learning, classification, regression, and visualization dashboards.',
        'month_3': 'Strategic Impact: A/B testing methodologies, executive storytelling, and automated ETL pipelines.'
    },
    'cloud_devops': {
        'title': 'Cloud Architecture & DevOps Track',
        'target_roles': ['DevOps Engineer', 'Cloud Architect', 'Site Reliability Engineer (SRE)'],
        'core_skills': ['Linux & Shell Scripting', 'Docker & Containers', 'Kubernetes', 'AWS / Cloud Fundamentals', 'Terraform (IaC)', 'CI/CD Pipelines'],
        'month_1': 'Infrastructure Basics: Linux system administration, shell scripting, and containerization with Docker.',
        'month_2': 'Cloud Infrastructure: AWS core services, infrastructure-as-code with Terraform, and CI/CD pipelines.',
        'month_3': 'Orchestration & Reliability: Kubernetes clusters, Prometheus/Grafana monitoring, and incident management.'
    },
    'cybersecurity': {
        'title': 'Cybersecurity & Defensive Engineering Track',
        'target_roles': ['Cybersecurity Analyst', 'Security Engineer', 'Penetration Tester'],
        'core_skills': ['Network Security & Protocols', 'Vulnerability Assessment', 'Ethical Hacking & Penetration Testing', 'SIEM & Threat Detection', 'Cryptography Basics', 'Web Application Security (OWASP)'],
        'month_1': 'Security Foundations: TCP/IP packet analysis, OSI model, Linux security, and defense-in-depth principles.',
        'month_2': 'Application Security: OWASP Top 10 web vulnerabilities, secure code reviews, and vulnerability scanners.',
        'month_3': 'Detection & Response: Incident triage, SIEM tool mastery, log correlation, and security compliance.'
    },
    'ui_ux': {
        'title': 'UI/UX & Product Design Track',
        'target_roles': ['Product Designer', 'UI/UX Designer', 'Design Systems Engineer'],
        'core_skills': ['User Research & Personas', 'Figma & Wireframing', 'Design Systems', 'Interactive Prototyping', 'Accessibility (WCAG)', 'Usability Testing'],
        'month_1': 'Research & IA: User interviews, journey mapping, empathy maps, and information architecture.',
        'month_2': 'Visual & Interaction Design: High-fidelity components in Figma, tokens, design systems, and micro-interactions.',
        'month_3': 'Testing & Delivery: Usability testing protocols, accessibility audits, and design-to-engineering handoff.'
    },
    'product_management': {
        'title': 'Product Management & Agile Leadership',
        'target_roles': ['Technical Product Manager', 'Product Manager', 'Scrum Product Owner'],
        'core_skills': ['Product Strategy & Vision', 'User Discovery & Research', 'Agile & Scrum Methodologies', 'Metrics & OKRs', 'Roadmapping & Prioritization', 'Stakeholder Management'],
        'month_1': 'Discovery & Validation: Problem statements, customer interviews, user persona synthesis, and market research.',
        'month_2': 'Delivery & Metrics: Writing crisp PRDs/user stories, backlog grooming, sprint planning, and North Star metrics.',
        'month_3': 'Strategic Leadership: Cross-functional alignment, product-led growth experiments, and executive roadmaps.'
    },
    'soft_skills': {
        'title': 'Executive Presence & Technical Leadership',
        'target_roles': ['Engineering Manager', 'Team Lead', 'Senior Technical Specialist'],
        'core_skills': ['Public Speaking & Presentation', 'Negotiation & Influence', 'Mentorship & Coaching', 'Conflict Resolution', 'Strategic Thinking', 'Cross-Functional Collaboration'],
        'month_1': 'Communication Clarity: Structuring ideas with the Pyramid Principle, active listening, and meeting facilitation.',
        'month_2': 'Influence & Collaboration: Navigating organizational dynamics, advocating for ideas, and peer mentorship.',
        'month_3': 'Executive Impact: High-stakes negotiation, salary advocacy, strategic technical vision, and thought leadership.'
    }
}


def get_or_create_user_profile(user):
    """Safely get or create UserProfile for user"""
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'target_role': 'Full-Stack Web Developer',
            'primary_interest': 'web_dev',
            'weekly_hours': 10,
            'experience_level': 'beginner'
        }
    )
    return profile


# ==============================================================================
# CORE PAGES
# ==============================================================================
def home(request):
    """Modern home landing page with real-time dynamic database metrics"""
    stats = {
        'skills_count': Skill.objects.filter(is_active=True).count(),
        'resources_count': LearningResource.objects.count(),
        'domains_count': len(Skill.DOMAIN_CHOICES) - 1,
    }
    top_skills = Skill.objects.filter(is_active=True).order_by('-market_demand', 'name')[:8]

    # Real-time preview calculation
    live_preview = {
        'is_personalized': False,
        'target_role': 'Full-Stack Web Developer',
        'match_score': 78,
        'milestones': []
    }

    if request.user.is_authenticated:
        profile = get_or_create_user_profile(request.user)
        rec = Recommendation.objects.filter(user_profile=profile, is_active=True).first()
        if not rec:
            rec = generate_hybrid_recommendation(profile)
        
        live_preview['is_personalized'] = True
        live_preview['target_role'] = rec.target_role or profile.target_role
        live_preview['match_score'] = round(rec.match_score)
        
        milestones = []
        for rs in rec.skills.select_related('skill')[:3]:
            milestones.append({
                'name': rs.skill.name,
                'icon': rs.skill.icon,
                'timeline': rs.timeline,
                'priority': rs.priority,
            })
        live_preview['milestones'] = milestones
    else:
        # Live market benchmark preview from database
        sample_skills = Skill.objects.filter(is_active=True, market_demand='Very High')[:3]
        milestones = []
        timelines = ['Month 1 (Core Foundations)', 'Month 2 (Applied Frameworks)', 'Month 3 (Mastery & Scale)']
        for idx, sk in enumerate(sample_skills):
            milestones.append({
                'name': sk.name,
                'icon': sk.icon,
                'timeline': timelines[idx] if idx < len(timelines) else 'Month 3',
                'priority': idx + 1,
            })
        live_preview['milestones'] = milestones

    return render(request, 'recommender/home.html', {
        'stats': stats,
        'top_skills': top_skills,
        'live_preview': live_preview,
        'domain_benchmarks': DOMAIN_BENCHMARKS
    })



def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            # Initialize profile
            get_or_create_user_profile(user)
            messages.success(request, f'Welcome to SkillHer, {username}! Your account is ready.')
            login(request, user)
            return redirect('skill_assessment')
    else:
        form = UserCreationForm()
    return render(request, 'recommender/register.html', {'form': form})


@login_required
def profile(request):
    """User profile view and edit"""
    user_profile = get_or_create_user_profile(request.user)

    if request.method == 'POST':
        user_profile.age = request.POST.get('age') or None
        user_profile.location = request.POST.get('location', '').strip()
        user_profile.education_level = request.POST.get('education_level', '').strip()
        user_profile.current_occupation = request.POST.get('current_occupation', '').strip()
        user_profile.target_role = request.POST.get('target_role', '').strip() or 'Full-Stack Web Developer'
        user_profile.primary_interest = request.POST.get('primary_interest', 'web_dev')
        user_profile.interests = request.POST.get('interests', '').strip()
        user_profile.goals = request.POST.get('goals', '').strip()
        
        try:
            user_profile.weekly_hours = int(request.POST.get('weekly_hours', 10))
        except (ValueError, TypeError):
            user_profile.weekly_hours = 10

        user_profile.experience_level = request.POST.get('experience_level', 'beginner')
        user_profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    # Get user's skills and assessment stats
    user_skills = UserSkill.objects.filter(user_profile=user_profile).select_related('skill')
    assessments = AssessmentResult.objects.filter(user_profile=user_profile)[:5]
    latest_rec = Recommendation.objects.filter(user_profile=user_profile, is_active=True).first()

    context = {
        'user_profile': user_profile,
        'user_skills': user_skills,
        'assessments': assessments,
        'latest_rec': latest_rec,
        'domains': Skill.DOMAIN_CHOICES,
        'experience_levels': UserProfile.EXPERIENCE_LEVELS,
    }
    return render(request, 'recommender/profile.html', context)


# ==============================================================================
# INTEREST-DRIVEN SKILL ASSESSMENT
# ==============================================================================
@login_required
def skill_assessment(request):
    """
    Skill assessment customized according to user's selected interest domain.
    Users can evaluate domain-specific skills and take scenario diagnostic quizzes.
    """
    user_profile = get_or_create_user_profile(request.user)

    # Active domain selected in URL param or defaulted to user's primary interest
    selected_domain = request.GET.get('domain', user_profile.primary_interest or 'web_dev')
    
    # Verify valid domain
    valid_domains = [d[0] for d in Skill.DOMAIN_CHOICES]
    if selected_domain not in valid_domains:
        selected_domain = 'web_dev'

    if request.method == 'POST':
        action = request.POST.get('action', 'save_skills')

        if action == 'save_skills':
            # Save or update selected skills for this domain
            domain_skills = Skill.objects.filter(
                Q(domain=selected_domain) | Q(domain='general'),
                is_active=True
            )

            updated_count = 0
            for skill in domain_skills:
                prof_key = f'skill_{skill.id}'
                years_key = f'years_{skill.id}'
                conf_key = f'confidence_{skill.id}'

                proficiency = request.POST.get(prof_key)
                if proficiency and proficiency in ['none', 'basic', 'intermediate', 'advanced', 'expert']:
                    years_val = request.POST.get(years_key)
                    conf_val = request.POST.get(conf_key, 50)
                    
                    try:
                        years_exp = float(years_val) if years_val else None
                    except (ValueError, TypeError):
                        years_exp = None

                    try:
                        conf_score = int(conf_val)
                    except (ValueError, TypeError):
                        conf_score = 50

                    user_skill, _ = UserSkill.objects.update_or_create(
                        user_profile=user_profile,
                        skill=skill,
                        defaults={
                            'proficiency_level': proficiency,
                            'years_experience': years_exp,
                            'confidence_score': conf_score,
                        }
                    )
                    updated_count += 1

            # Update user's profile primary interest
            user_profile.primary_interest = selected_domain
            user_profile.save(update_fields=['primary_interest', 'updated_at'])

            # Automatically trigger real-time recommendation synthesis
            generate_hybrid_recommendation(user_profile, selected_domain)

            messages.success(request, f'Skill assessment saved! Recommendations for {user_profile.get_primary_interest_display()} are now generated.')
            return redirect('view_recommendations')

        elif action == 'submit_quiz':
            # Handle scenario quiz submission
            questions = AssessmentQuestion.objects.filter(domain=selected_domain)
            total = questions.count()
            correct = 0

            for q in questions:
                user_choice = request.POST.get(f'q_{q.id}', '').strip().lower()
                if user_choice == q.correct_option.lower():
                    correct += 1
                    # If skill is linked, elevate proficiency to at least intermediate
                    if q.skill:
                        us, _ = UserSkill.objects.get_or_create(
                            user_profile=user_profile,
                            skill=q.skill,
                            defaults={'proficiency_level': 'intermediate'}
                        )
                        if us.proficiency_level in ['none', 'basic']:
                            us.proficiency_level = 'intermediate'
                            us.confidence_score = 75
                            us.save()

            score_pct = round((correct / total * 100) if total > 0 else 0, 1)
            
            if score_pct >= 85:
                level_name = 'Advanced / Senior'
            elif score_pct >= 60:
                level_name = 'Intermediate'
            elif score_pct >= 35:
                level_name = 'Developing'
            else:
                level_name = 'Foundational Beginner'

            result = AssessmentResult.objects.create(
                user_profile=user_profile,
                domain=selected_domain,
                total_questions=total,
                correct_answers=correct,
                score_percentage=score_pct,
                assessed_level=level_name,
                feedback_summary=f"Scored {correct}/{total} ({score_pct}%) in {dict(Skill.DOMAIN_CHOICES).get(selected_domain, selected_domain)} assessment."
            )

            # Auto regenerate recommendations
            generate_hybrid_recommendation(user_profile, selected_domain)

            messages.success(request, f"Assessment completed! Score: {score_pct}% ({level_name}). Your recommendations have been updated.")
            return redirect('view_recommendations')

    # Fetch skills for this specific domain + general core skills
    skills_for_domain = Skill.objects.filter(
        Q(domain=selected_domain) | Q(domain='general'),
        is_active=True
    ).order_by('domain', 'difficulty_level', 'name')

    # Fetch questions for this domain
    questions = AssessmentQuestion.objects.filter(domain=selected_domain)

    # Get user's current saved skills for pre-population
    user_skills_dict = {}
    for us in UserSkill.objects.filter(user_profile=user_profile).select_related('skill'):
        user_skills_dict[us.skill.id] = {
            'proficiency': us.proficiency_level,
            'years': us.years_experience or '',
            'confidence': us.confidence_score,
        }

    # Latest assessment in this domain
    latest_result = AssessmentResult.objects.filter(user_profile=user_profile, domain=selected_domain).first()

    context = {
        'user_profile': user_profile,
        'selected_domain': selected_domain,
        'domain_label': dict(Skill.DOMAIN_CHOICES).get(selected_domain, selected_domain),
        'domain_choices': Skill.DOMAIN_CHOICES,
        'skills': skills_for_domain,
        'user_skills': user_skills_dict,
        'questions': questions,
        'latest_result': latest_result,
        'benchmark_info': DOMAIN_BENCHMARKS.get(selected_domain, DOMAIN_BENCHMARKS['web_dev'])
    }
    return render(request, 'recommender/skill_assessment.html', context)


# ==============================================================================
# REAL-TIME RECOMMENDATION ENGINE (HYBRID: MARKET-BENCHMARK + GROQ LLM)
# ==============================================================================
def calculate_realtime_metrics(user_profile, domain=None):
    """
    Computes real-time match readiness score, top skill gaps, and milestone plan.
    Returns structured dictionary with instantaneous response time.
    """
    domain = domain or user_profile.primary_interest or 'web_dev'
    benchmark = DOMAIN_BENCHMARKS.get(domain, DOMAIN_BENCHMARKS['web_dev'])

    domain_skills = Skill.objects.filter(Q(domain=domain) | Q(domain='general'), is_active=True)
    user_skills_map = {
        us.skill_id: us for us in UserSkill.objects.filter(user_profile=user_profile)
    }

    scored_skills = []
    total_benchmark_points = len(domain_skills) * 4 if domain_skills.exists() else 20
    current_earned_points = 0

    points_map = {'none': 0, 'basic': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}

    for skill in domain_skills:
        user_skill = user_skills_map.get(skill.id)
        prof = user_skill.proficiency_level if user_skill else 'none'
        pts = points_map.get(prof, 0)
        current_earned_points += pts

        # Deficit gap (0 = fully mastered, 4 = urgent missing gap)
        gap_deficit = 4 - pts
        scored_skills.append({
            'skill': skill,
            'current_proficiency': prof,
            'gap_deficit': gap_deficit,
            'market_demand': skill.market_demand,
        })

    # Sort gaps: highest deficit and very high demand first
    scored_skills.sort(key=lambda s: (s['gap_deficit'], s['market_demand'] == 'Very High'), reverse=True)

    match_percentage = round((current_earned_points / total_benchmark_points * 100) if total_benchmark_points > 0 else 50, 1)
    match_percentage = min(max(match_percentage, 15.0), 98.0) # realistic bounds

    return {
        'domain': domain,
        'benchmark': benchmark,
        'match_score': match_percentage,
        'scored_skills': scored_skills,
    }


def generate_hybrid_recommendation(user_profile, domain=None):
    """
    Creates or updates the active recommendation with real-time gap analysis and learning path.
    Integrates Groq LLM when available, and provides instant deterministic AI synthesis.
    """
    domain = domain or user_profile.primary_interest or 'web_dev'
    metrics = calculate_realtime_metrics(user_profile, domain)
    benchmark = metrics['benchmark']
    scored_skills = metrics['scored_skills']

    # Archive previous recommendations of same type for cleanliness
    Recommendation.objects.filter(user_profile=user_profile, is_active=True).update(is_active=False)

    target_role = user_profile.target_role or benchmark['target_roles'][0]

    # Create recommendation record
    rec_title = f"{target_role} Acceleration Roadmap"
    rec_desc = f"Tailored skill development strategy designed for {target_role} in {dict(Skill.DOMAIN_CHOICES).get(domain, domain)}. Calculated based on your current assessment, availability of {user_profile.weekly_hours} hrs/week, and high-demand market competencies."

    recommendation = Recommendation.objects.create(
        user_profile=user_profile,
        recommendation_type='realtime_roadmap',
        title=rec_title,
        description=rec_desc,
        target_role=target_role,
        match_score=metrics['match_score'],
        generated_by_llm=False,
        groq_model_used='Real-Time Engine'
    )

    # Top 3-5 skill gaps to bridge
    top_gaps = scored_skills[:5]
    timelines = ['Month 1 (Core Foundations)', 'Month 1 (Tooling)', 'Month 2 (Applied Frameworks)', 'Month 2 (Integration)', 'Month 3 (Mastery & Portfolio)']

    for i, item in enumerate(top_gaps):
        sk = item['skill']
        timeline = timelines[i] if i < len(timelines) else 'Month 3'
        
        reasoning = (
            f"High market demand skill for {target_role}. "
            f"Your current level is {item['current_proficiency'].title()}. "
            f"Focusing on {sk.name} unlocks pivotal competencies for career progression."
        )

        RecommendationSkill.objects.create(
            recommendation=recommendation,
            skill=sk,
            priority=i + 1,
            timeline=timeline,
            reasoning=reasoning,
            status='todo'
        )

        # Attach top learning resources for this skill
        resources = LearningResource.objects.filter(skill=sk)[:2]
        for res in resources:
            RecommendationResource.objects.get_or_create(
                recommendation=recommendation,
                resource=res,
                defaults={'relevance_score': 0.95 - (i * 0.05)}
            )

    # Live Real-Time Groq LLM Generation
    groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
    if groq_api_key:
        try:
            current_skills_summary = [f"{item['skill'].name} ({item['current_proficiency']})" for item in scored_skills[:6]]
            prompt = f"""
            You are a real-time AI career intelligence mentor specializing in women's technical career advancement.
            Analyze this live profile:
            - Target Career Role: {target_role}
            - Focus Domain: {dict(Skill.DOMAIN_CHOICES).get(domain, domain)}
            - Weekly Study Hours: {user_profile.weekly_hours} hours/week
            - Assessed Competencies: {current_skills_summary}
            
            Provide tailored real-time career advice for women in technology pursuing {target_role}:
            1. Executive summary of immediate competitive advantages and high-leverage growth areas.
            2. Strategic career guidance covering portfolio visibility, technical credibility, and compensation advocacy.
            3. Recommended focus for the next 90 days.
            Keep the advice inspiring, highly specific, and actionable.
            """

            # Active supported models on Groq
            models_to_try = ['openai/gpt-oss-20b', 'openai/gpt-oss-120b', 'qwen/qwen3.8-27b']
            llm_text = None
            model_used_name = None

            for model_candidate in models_to_try:
                try:
                    response = requests.post(
                        'https://api.groq.com/openai/v1/chat/completions',
                        headers={'Authorization': f'Bearer {groq_api_key}', 'Content-Type': 'application/json'},
                        json={
                            'model': model_candidate,
                            'messages': [
                                {'role': 'system', 'content': 'You are an inspiring, authoritative AI career advisor for women in technology.'},
                                {'role': 'user', 'content': prompt}
                            ],
                            'max_tokens': 700,
                            'temperature': 0.6
                        },
                        timeout=10
                    )
                    if response.status_code == 200:
                        res_json = response.json()
                        llm_text = res_json['choices'][0]['message']['content'].strip()
                        model_used_name = model_candidate
                        break
                except Exception:
                    continue

            if llm_text:
                recommendation.description = f"{rec_desc}\n\n### Strategic AI Career Guidance ({model_used_name}):\n{llm_text}"
                recommendation.generated_by_llm = True
                recommendation.groq_model_used = f"Groq / {model_used_name.split('/')[-1].upper()} (Live)"
                recommendation.save(update_fields=['description', 'generated_by_llm', 'groq_model_used'])
        except Exception:
            # Graceful fallback: maintain fast response without failing
            pass

    return recommendation


@login_required
def get_recommendations(request):
    """Regenerate recommendations and redirect to view"""
    user_profile = get_or_create_user_profile(request.user)
    selected_domain = request.GET.get('domain', user_profile.primary_interest)
    generate_hybrid_recommendation(user_profile, selected_domain)
    messages.success(request, 'Recommendations freshly synthesized with real-time data!')
    return redirect('view_recommendations')


@login_required
def view_recommendations(request):
    """
    Main Recommendations Dashboard with real-time UI controls and roadmap.
    """
    user_profile = get_or_create_user_profile(request.user)
    
    # Get active recommendation or generate on first visit
    recommendation = Recommendation.objects.filter(user_profile=user_profile, is_active=True).first()
    if not recommendation:
        recommendation = generate_hybrid_recommendation(user_profile)

    # Get related skills and resources
    rec_skills = RecommendationSkill.objects.filter(recommendation=recommendation).select_related('skill')
    rec_resources = RecommendationResource.objects.filter(recommendation=recommendation).select_related('resource__skill')

    # User's current skill matrix for progress radar
    user_skills = UserSkill.objects.filter(user_profile=user_profile).select_related('skill')

    all_recommendations = Recommendation.objects.filter(user_profile=user_profile).order_by('-created_at')[:5]

    context = {
        'user_profile': user_profile,
        'recommendation': recommendation,
        'rec_skills': rec_skills,
        'rec_resources': rec_resources,
        'user_skills': user_skills,
        'all_recommendations': all_recommendations,
        'domains': Skill.DOMAIN_CHOICES,
        'benchmark': DOMAIN_BENCHMARKS.get(user_profile.primary_interest, DOMAIN_BENCHMARKS['web_dev'])
    }
    return render(request, 'recommender/recommendations.html', context)


@login_required
def recommendation_detail(request, rec_id):
    """View details of a specific recommendation"""
    recommendation = get_object_or_404(Recommendation, id=rec_id, user_profile__user=request.user)
    rec_skills = RecommendationSkill.objects.filter(recommendation=recommendation).select_related('skill')
    rec_resources = RecommendationResource.objects.filter(recommendation=recommendation).select_related('resource__skill')

    context = {
        'recommendation': recommendation,
        'recommendation_skills': rec_skills,
        'recommendation_resources': rec_resources,
    }
    return render(request, 'recommender/recommendation_detail.html', context)


# ==============================================================================
# REAL-TIME ASYNC APIS (FOR INSTANT DYNAMIC UI UPDATES)
# ==============================================================================
@login_required
@require_http_methods(["GET", "POST"])
def realtime_recommendations_api(request):
    """
    Instant JSON API for real-time recommendation updates as user changes inputs.
    No page reload required!
    """
    user_profile = get_or_create_user_profile(request.user)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST

        domain = data.get('domain', user_profile.primary_interest)
        target_role = data.get('target_role', user_profile.target_role)
        weekly_hours = data.get('weekly_hours')

        if target_role:
            user_profile.target_role = target_role
        if domain:
            user_profile.primary_interest = domain
        if weekly_hours:
            try:
                user_profile.weekly_hours = int(weekly_hours)
            except (ValueError, TypeError):
                pass
        user_profile.save()
    else:
        domain = request.GET.get('domain', user_profile.primary_interest)

    # Compute instant metrics and regenerate
    rec = generate_hybrid_recommendation(user_profile, domain)
    rec_skills = RecommendationSkill.objects.filter(recommendation=rec).select_related('skill')
    rec_resources = RecommendationResource.objects.filter(recommendation=rec).select_related('resource__skill')

    skills_payload = []
    for rs in rec_skills:
        skills_payload.append({
            'id': rs.id,
            'name': rs.skill.name,
            'category': rs.skill.get_category_display(),
            'domain': rs.skill.get_domain_display(),
            'difficulty': rs.skill.get_difficulty_level_display(),
            'market_demand': rs.skill.market_demand,
            'icon': rs.skill.icon,
            'priority': rs.priority,
            'timeline': rs.timeline,
            'reasoning': rs.reasoning,
            'status': rs.status,
        })

    resources_payload = []
    for rr in rec_resources:
        resources_payload.append({
            'title': rr.resource.title,
            'url': rr.resource.url,
            'type': rr.resource.get_resource_type_display(),
            'provider': rr.resource.provider,
            'skill': rr.resource.skill.name,
            'rating': rr.resource.rating,
            'duration_hours': rr.resource.duration_hours,
            'is_free': rr.resource.is_free,
        })

    return JsonResponse({
        'status': 'success',
        'title': rec.title,
        'description': rec.description,
        'target_role': rec.target_role,
        'match_score': rec.match_score,
        'domain': domain,
        'domain_label': dict(Skill.DOMAIN_CHOICES).get(domain, domain),
        'skills': skills_payload,
        'resources': resources_payload,
    })


@login_required
@require_POST
def toggle_skill_status_api(request):
    """Toggle a recommended skill status in real-time (todo -> in_progress -> completed)"""
    try:
        data = json.loads(request.body)
        rec_skill_id = data.get('rec_skill_id')
        new_status = data.get('status')
        
        rec_skill = get_object_or_404(
            RecommendationSkill,
            id=rec_skill_id,
            recommendation__user_profile__user=request.user
        )
        
        if new_status in ['todo', 'in_progress', 'completed']:
            rec_skill.status = new_status
            rec_skill.save(update_fields=['status'])
            
            # If completed, also elevate user's UserSkill proficiency level!
            if new_status == 'completed':
                us, _ = UserSkill.objects.get_or_create(
                    user_profile=rec_skill.recommendation.user_profile,
                    skill=rec_skill.skill
                )
                us.proficiency_level = 'advanced'
                us.confidence_score = 90
                us.save()

            return JsonResponse({'status': 'success', 'new_status': rec_skill.status})
        return HttpResponseBadRequest("Invalid status")
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def resources(request):
    """View and filter all curated learning resources"""
    resources_list = LearningResource.objects.select_related('skill').all()

    # Filters
    selected_domain = request.GET.get('domain')
    selected_type = request.GET.get('type')
    selected_skill = request.GET.get('skill')
    free_only = request.GET.get('free')

    if selected_domain:
        resources_list = resources_list.filter(skill__domain=selected_domain)
    if selected_type:
        resources_list = resources_list.filter(resource_type=selected_type)
    if selected_skill:
        resources_list = resources_list.filter(skill_id=selected_skill)
    if free_only == '1':
        resources_list = resources_list.filter(is_free=True)

    skills = Skill.objects.filter(is_active=True).order_by('name')

    context = {
        'resources': resources_list,
        'skills': skills,
        'domains': Skill.DOMAIN_CHOICES,
        'resource_types': LearningResource.RESOURCE_TYPES,
        'selected_domain': selected_domain,
        'selected_type': selected_type,
        'selected_skill': selected_skill,
        'free_only': free_only,
    }
    return render(request, 'recommender/resources.html', context)


def about(request):
    """About page view"""
    return render(request, 'recommender/about.html')


def logout_view(request):
    """Secure logout view with dedicated confirmation page"""
    if request.user.is_authenticated:
        auth_logout(request)
    return render(request, 'recommender/logout.html')


def send_email_via_nodemailer(payload):
    """
    Invokes the Node.js Nodemailer script (mailer.js) to dispatch email.
    Returns (success: bool, info: dict)
    """
    mailer_script = os.path.join(settings.BASE_DIR, 'mailer.js')
    if not os.path.exists(mailer_script):
        return False, {'message': 'mailer.js script not found'}

    try:
        proc = subprocess.run(
            ['node', mailer_script, json.dumps(payload)],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=settings.BASE_DIR
        )
        if proc.returncode == 0:
            try:
                res_data = json.loads(proc.stdout.strip())
                return True, res_data
            except json.JSONDecodeError:
                return True, {'raw_output': proc.stdout}
        else:
            return False, {'error': proc.stderr or proc.stdout}
    except Exception as e:
        return False, {'error': str(e)}


def contact(request):
    """
    Contact Us page view supporting both standard POST and AJAX submissions via Nodemailer.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        category = request.POST.get('category', 'general')
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        if not name or not email or not subject or not message_text:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'recommender/contact.html', {
                'categories': ContactMessage.CATEGORY_CHOICES,
                'form_data': request.POST
            })

        payload = {
            'name': name,
            'email': email,
            'category': dict(ContactMessage.CATEGORY_CHOICES).get(category, category),
            'subject': subject,
            'message': message_text,
        }

        # Dispatch email via Nodemailer
        success, info = send_email_via_nodemailer(payload)
        msg_id = info.get('messageId', '') if success else ''

        # Save to database
        ContactMessage.objects.create(
            name=name,
            email=email,
            category=category,
            subject=subject,
            message=message_text,
            sent_via_nodemailer=success,
            nodemailer_message_id=msg_id
        )

        messages.success(request, 'Your message has been sent successfully via Nodemailer! Our team will get back to you shortly.')
        return redirect('contact')

    context = {
        'categories': ContactMessage.CATEGORY_CHOICES,
    }
    return render(request, 'recommender/contact.html', context)


@require_POST
def api_contact(request):
    """
    JSON API endpoint for instant AJAX contact form submissions via Nodemailer.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    category = data.get('category', 'general')
    subject = data.get('subject', '').strip()
    message_text = data.get('message', '').strip()

    if not name or not email or not subject or not message_text:
        return JsonResponse({'status': 'error', 'message': 'All fields are required.'}, status=400)

    payload = {
        'name': name,
        'email': email,
        'category': dict(ContactMessage.CATEGORY_CHOICES).get(category, category),
        'subject': subject,
        'message': message_text,
    }

    success, info = send_email_via_nodemailer(payload)
    msg_id = info.get('messageId', '') if success else ''

    ContactMessage.objects.create(
        name=name,
        email=email,
        category=category,
        subject=subject,
        message=message_text,
        sent_via_nodemailer=success,
        nodemailer_message_id=msg_id
    )

    return JsonResponse({
        'status': 'success',
        'message': 'Message sent successfully via Nodemailer!',
        'messageId': msg_id,
        'preview': info.get('preview', '')
    })