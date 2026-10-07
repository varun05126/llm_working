from django.contrib import admin
from .models import (
    UserProfile, Skill, UserSkill, AssessmentQuestion,
    AssessmentResult, LearningResource, Recommendation,
    RecommendationSkill, RecommendationResource
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_role', 'primary_interest', 'experience_level', 'weekly_hours', 'created_at')
    list_filter = ('primary_interest', 'experience_level', 'created_at')
    search_fields = ('user__username', 'user__email', 'target_role', 'current_occupation', 'location')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'category', 'difficulty_level', 'market_demand', 'is_active')
    list_filter = ('domain', 'category', 'difficulty_level', 'market_demand', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('market_demand', 'is_active')

@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'skill', 'proficiency_level', 'years_experience', 'confidence_score', 'last_updated')
    list_filter = ('proficiency_level', 'skill__domain', 'last_updated')
    search_fields = ('user_profile__user__username', 'skill__name')

@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'domain', 'skill', 'difficulty', 'correct_option', 'created_at')
    list_filter = ('domain', 'difficulty', 'correct_option')
    search_fields = ('question_text', 'explanation')

@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'domain', 'score_percentage', 'assessed_level', 'correct_answers', 'total_questions', 'created_at')
    list_filter = ('domain', 'assessed_level', 'created_at')
    search_fields = ('user_profile__user__username', 'feedback_summary')

@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'skill', 'provider', 'difficulty_level', 'rating', 'is_free')
    list_filter = ('resource_type', 'difficulty_level', 'is_free', 'skill__domain')
    search_fields = ('title', 'description', 'url', 'provider')
    list_editable = ('is_free', 'rating')

class RecommendationSkillInline(admin.TabularInline):
    model = RecommendationSkill
    extra = 1

class RecommendationResourceInline(admin.TabularInline):
    model = RecommendationResource
    extra = 1

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_profile', 'recommendation_type', 'match_score', 'generated_by_llm', 'is_active', 'created_at')
    list_filter = ('recommendation_type', 'generated_by_llm', 'is_active', 'created_at')
    search_fields = ('user_profile__user__username', 'title', 'description', 'target_role')
    inlines = [RecommendationSkillInline, RecommendationResourceInline]