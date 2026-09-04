from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
import requests
from .models import UserProfile, Skill, UserSkill, LearningResource, Recommendation, RecommendationSkill, RecommendationResource
from django.conf import settings

def home(request):
    """Home page view"""
    return render(request, 'recommender/home.html')

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('profile')
    else:
        form = UserCreationForm()
    return render(request, 'recommender/register.html', {'form': form})

@login_required
def profile(request):
    """User profile view and edit"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_profile.age = request.POST.get('age') or None
        user_profile.location = request.POST.get('location', '')
        user_profile.education_level = request.POST.get('education_level', '')
        user_profile.current_occupation = request.POST.get('current_occupation', '')
        user_profile.interests = request.POST.get('interests', '')
        user_profile.goals = request.POST.get('goals', '')
        user_profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    # Get user's skills
    user_skills = UserSkill.objects.filter(user_profile=user_profile).select_related('skill')

    context = {
        'user_profile': user_profile,
        'user_skills': user_skills,
    }
    return render(request, 'recommender/profile.html', context)

@login_required
def skill_assessment(request):
    """Skill assessment view"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    skills = Skill.objects.filter(is_active=True)

    if request.method == 'POST':
        # Process skill assessment form
        for skill in skills:
            proficiency = request.POST.get(f'skill_{skill.id}')
            years_exp = request.POST.get(f'years_{skill.id}')

            if proficiency:
                user_skill, created = UserSkill.objects.get_or_create(
                    user_profile=user_profile,
                    skill=skill,
                    defaults={
                        'proficiency_level': proficiency,
                        'years_experience': years_exp if years_exp else None
                    }
                )
                if not created:
                    user_skill.proficiency_level = proficiency
                    user_skill.years_experience = years_exp if years_exp else None
                    user_skill.save()

        messages.success(request, 'Skill assessment saved!')
        return redirect('get_recommendations')

    # Get user's current skills for pre-populating form
    user_skills = {}
    for us in UserSkill.objects.filter(user_profile=user_profile):
        user_skills[us.skill.id] = {
            'proficiency': us.proficiency_level,
            'years': us.years_experience
        }

    context = {
        'skills': skills,
        'user_skills': user_skills,
    }
    return render(request, 'recommender/skill_assessment.html', context)

@login_required
def get_recommendations(request):
    """Generate skill recommendations using Groq LLM"""
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Get user's current skills
    user_skills = UserSkill.objects.filter(user_profile=user_profile).select_related('skill')

    # Prepare data for LLM prompt
    user_info = {
        'age': user_profile.age,
        'location': user_profile.location,
        'education': user_profile.education_level,
        'occupation': user_profile.current_occupation,
        'interests': user_profile.interests,
        'goals': user_profile.goals,
    }

    skills_data = []
    for us in user_skills:
        skills_data.append({
            'skill': us.skill.name,
            'category': us.skill.category,
            'proficiency': us.proficiency_level,
            'years_experience': us.years_experience
        })

    # Generate recommendations using Groq API
    recommendations = []
    if request.method == 'POST' or True:  # Always generate for demo
        try:
            # Call Groq API
            groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
            if groq_api_key:
                # Prepare prompt for skill gap analysis and learning path
                prompt = f"""
                As a career development advisor for women, analyze the following profile and provide skill development recommendations:

                User Profile:
                - Age: {user_info['age'] or 'Not specified'}
                - Location: {user_info['location'] or 'Not specified'}
                - Education: {user_info['education'] or 'Not specified'}
                - Current Occupation: {user_info['occupation'] or 'Not specified'}
                - Interests: {user_info['interests'] or 'Not specified'}
                - Goals: {user_info['goals'] or 'Not specified'}

                Current Skills:
                {json.dumps(skills_data, indent=2)}

                Please provide:
                1. Top 3 skill gaps to focus on for career advancement
                2. A 3-month learning path with recommended resources
                3. Specific advice for women in tech/leadership roles

                Format the response as JSON with the following structure:
                {{
                    "skill_gaps": [
                        {{"skill": "skill_name", "reasoning": "explanation", "priority": 1}}
                    ],
                    "learning_path": [
                        {{"skill": "skill_name", "resources": [{{"title": "resource_title", "type": "course/tutorial/etc", "url": "resource_url"}}], "timeline": "month_1"}}
                    ],
                    "career_advice": "specific advice for women's career development"
                }}
                """

                # Call the actual Groq API
                headers = {
                    'Authorization': f'Bearer {groq_api_key}',
                    'Content-Type': 'application/json'
                }
                data = {
                    'model': 'llama2-70b-4096',  # Changed from decommissioned model to a supported one
                    'messages': [
                        {'role': 'system', 'content': 'You are a career development advisor specializing in women\'s skill development.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.7,
                    'max_tokens': 2000
                }
                try:
                    response = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=data, timeout=30)
                    response.raise_for_status()  # Raises an HTTPError for bad responses
                    result = response.json()
                    llm_response = result['choices'][0]['message']['content']
                except requests.exceptions.RequestException as e:
                    messages.warning(request, f'Groq API request failed: {str(e)}. Using demo recommendations.')
                    return _create_demo_recommendations(request, user_profile)
                except (KeyError, IndexError, json.JSONDecodeError) as e:
                    messages.warning(request, f'Error parsing Groq API response: {str(e)}. Using demo recommendations.')
                    return _create_demo_recommendations(request, user_profile)

                # Parse the LLM response
                try:
                    llm_data = json.loads(llm_response)
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    llm_data = {
                        "skill_gaps": [
                            {
                                "skill": "Communication",
                                "reasoning": "Strong communication skills are vital for career advancement.",
                                "priority": 1
                            }
                        ],
                        "learning_path": [],
                        "career_advice": "Continue developing your skills and seek opportunities for growth."
                    }

                # Save recommendations to database
                # Clear old recommendations for this user
                Recommendation.objects.filter(user_profile=user_profile, is_active=True).update(is_active=False)

                # Create skill gap recommendation
                skill_gap_rec = Recommendation.objects.create(
                    user_profile=user_profile,
                    recommendation_type='skill_gap',
                    title='Skill Gap Analysis',
                    description='Analysis of skills to develop for career advancement',
                    generated_by_llm=True,
                    groq_model_used='llama2-70b-4096'  # Updated to reflect the model used
                )

                # Add skills to skill gap recommendation
                for i, gap in enumerate(llm_data.get('skill_gaps', [])):
                    try:
                        skill_obj = Skill.objects.get(name__iexact=gap['skill'])
                        RecommendationSkill.objects.create(
                            recommendation=skill_gap_rec,
                            skill=skill_obj,
                            priority=i+1,
                            reasoning=gap.get('reasoning', '')
                        )
                    except Skill.DoesNotExist:
                        # Create skill if it doesn't exist
                        skill_obj = Skill.objects.create(
                            name=gap['skill'],
                            category='other',
                            description=f"Skill related to {gap['skill']}",
                            difficulty_level='beginner'
                        )
                        RecommendationSkill.objects.create(
                            recommendation=skill_gap_rec,
                            skill=skill_obj,
                            priority=i+1,
                            reasoning=gap.get('reasoning', '')
                        )

                # Create learning path recommendation
                learning_path_rec = Recommendation.objects.create(
                    user_profile=user_profile,
                    recommendation_type='learning_path',
                    title='Personalized Learning Path',
                    description='3-month learning plan to develop recommended skills',
                    generated_by_llm=True,
                    groq_model_used='llama2-70b-4096'  # Updated to reflect the model used
                )

                # Add skills and resources to learning path recommendation
                for i, path_item in enumerate(llm_data.get('learning_path', [])):
                    try:
                        skill_obj = Skill.objects.get(name__iexact=path_item['skill'])
                        rec_skill = RecommendationSkill.objects.create(
                            recommendation=learning_path_rec,
                            skill=skill_obj,
                            priority=i+1,
                            reasoning=f"Part of {path_item.get('timeline', 'learning plan')}"
                        )

                        # Add resources
                        for resource_data in path_item.get('resources', []):
                            # Create or get learning resource
                            resource_obj, created = LearningResource.objects.get_or_create(
                                title=resource_data['title'],
                                defaults={
                                    'description': f"Learn about {resource_data['title']}",
                                    'resource_type': resource_data.get('type', 'course'),
                                    'url': resource_data['url'],
                                    'skill': skill_obj,
                                    'difficulty_level': 'beginner',
                                    'is_free': True
                                }
                            )
                            RecommendationResource.objects.create(
                                recommendation=learning_path_rec,
                                resource=resource_obj,
                                relevance_score=0.9
                            )
                    except Skill.DoesNotExist:
                        pass  # Skip if skill doesn't exist

                # Create career advice recommendation
                career_advice_rec = Recommendation.objects.create(
                    user_profile=user_profile,
                    recommendation_type='career_advice',
                    title='Career Development Advice',
                    description='Personalized advice for women\'s career growth',
                    generated_by_llm=True,
                    groq_model_used='llama2-70b-4096'  # Updated to reflect the model used
                )

                # For career advice, we might not link to specific skills/resources, or we could link to soft skills
                try:
                    comm_skill = Skill.objects.get(name__iexact='Communication')
                    RecommendationSkill.objects.create(
                        recommendation=career_advice_rec,
                        skill=comm_skill,
                        priority=1,
                        reasoning="Communication is key for career advice implementation"
                    )
                except Skill.DoesNotExist:
                    pass

                messages.success(request, 'Recommendations generated successfully!')
                return redirect('view_recommendations')

            else:
                messages.warning(request, 'Groq API key not configured. Using demo recommendations.')
                # Create demo recommendations without API call
                return _create_demo_recommendations(request, user_profile)

        except Exception as e:
            messages.error(request, f'Error generating recommendations: {str(e)}')
            # Fallback to demo recommendations
            return _create_demo_recommendations(request, user_profile)

    # Show existing recommendations
    return redirect('view_recommendations')

def _create_demo_recommendations(request, user_profile):
    """Create demo recommendations when API is not available"""
    # Clear old recommendations
    Recommendation.objects.filter(user_profile=user_profile, is_active=True).update(is_active=False)

    # Create skill gap recommendation
    skill_gap_rec = Recommendation.objects.create(
        user_profile=user_profile,
        recommendation_type='skill_gap',
        title='Skill Gap Analysis',
        description='Analysis of skills to develop for career advancement (Demo)',
        generated_by_llm=False,
        groq_model_used='demo'
    )

    # Add some demo skills
    demo_skills = [
        ('Data Analysis', 'Analytical skills for interpreting data and making informed decisions', 1),
        ('Project Management', 'Skills for planning, executing, and overseeing projects', 2),
        ('Digital Marketing', 'Online marketing strategies and tactics', 3)
    ]

    for skill_name, description, priority in demo_skills:
        skill_obj, created = Skill.objects.get_or_create(
            name=skill_name,
            defaults={
                'category': 'technical' if skill_name == 'Data Analysis' else 'business',
                'description': description,
                'difficulty_level': 'beginner'
            }
        )
        RecommendationSkill.objects.create(
            recommendation=skill_gap_rec,
            skill=skill_obj,
            priority=priority,
            reasoning=f"Important skill for career advancement in {user_profile.current_occupation or 'your field'}"
        )

    # Create learning path recommendation
    learning_path_rec = Recommendation.objects.create(
        user_profile=user_profile,
        recommendation_type='learning_path',
        title='Personalized Learning Path',
        description='3-month learning plan to develop recommended skills (Demo)',
        generated_by_llm=False,
        groq_model_used='demo'
    )

    # Add learning path skills with demo resources
    for i, (skill_name, description, _) in enumerate(demo_skills[:2]):  # First two skills
        skill_obj = Skill.objects.get(name=skill_name)
        rec_skill = RecommendationSkill.objects.create(
            recommendation=learning_path_rec,
            skill=skill_obj,
            priority=i+1,
            reasoning=f"Part of 3-month learning plan"
        )

        # Add demo resources
        resource_titles = [
            f"Introduction to {skill_name}",
            f"Advanced {skill_name} Techniques"
        ]
        for j, title in enumerate(resource_titles):
            resource_obj, created = LearningResource.objects.get_or_create(
                title=title,
                defaults={
                    'description': f"Comprehensive guide to {title}",
                    'resource_type': 'course' if j == 0 else 'tutorial',
                    'url': f"https://example.com/{skill_name.lower().replace(' ', '-')}-{j+1}",
                    'skill': skill_obj,
                    'difficulty_level': 'beginner' if j == 0 else 'intermediate',
                    'is_free': True
                }
            )
            RecommendationResource.objects.create(
                recommendation=learning_path_rec,
                resource=resource_obj,
                relevance_score=0.9 - (j * 0.1)
            )

    # Create career advice recommendation
    career_advice_rec = Recommendation.objects.create(
        user_profile=user_profile,
        recommendation_type='career_advice',
        title='Career Development Advice',
        description='Personalized advice for women\'s career growth (Demo)',
        generated_by_llm=False,
        groq_model_used='demo'
    )

    try:
        comm_skill = Skill.objects.get(name__iexact='Communication')
        RecommendationSkill.objects.create(
            recommendation=career_advice_rec,
            skill=comm_skill,
            priority=1,
            reasoning="Effective communication is essential for career success"
        )
    except Skill.DoesNotExist:
        pass

    messages.success(request, 'Demo recommendations generated!')
    return redirect('view_recommendations')

@login_required
def view_recommendations(request):
    """View all recommendations for the user"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    recommendations = Recommendation.objects.filter(user_profile=user_profile, is_active=True).order_by('-created_at')

    context = {
        'user_profile': user_profile,
        'recommendations': recommendations,
    }
    return render(request, 'recommender/recommendations.html', context)

@login_required
def recommendation_detail(request, rec_id):
    """View details of a specific recommendation"""
    recommendation = get_object_or_404(Recommendation, id=rec_id, user_profile__user=request.user, is_active=True)

    # Get related skills and resources
    recommendation_skills = RecommendationSkill.objects.filter(recommendation=recommendation).select_related('skill')
    recommendation_resources = RecommendationResource.objects.filter(recommendation=recommendation).select_related('resource__skill')

    context = {
        'recommendation': recommendation,
        'recommendation_skills': recommendation_skills,
        'recommendation_resources': recommendation_resources,
    }
    return render(request, 'recommender/recommendation_detail.html', context)

@login_required
def resources(request):
    """View all learning resources"""
    resources_list = LearningResource.objects.all().select_related('skill')

    # Filter by skill if requested
    skill_id = request.GET.get('skill')
    if skill_id:
        resources_list = resources_list.filter(skill_id=skill_id)

    # Filter by resource type
    resource_type = request.GET.get('type')
    if resource_type:
        resources_list = resources_list.filter(resource_type=resource_type)

    skills = Skill.objects.filter(is_active=True)
    resource_types = LearningResource.RESOURCE_TYPES

    context = {
        'resources': resources_list,
        'skills': skills,
        'resource_types': resource_types,
        'selected_skill': skill_id,
        'selected_type': resource_type,
    }
    return render(request, 'recommender/resources.html', context)

def about(request):
    """About page"""
    return render(request, 'recommender/about.html')