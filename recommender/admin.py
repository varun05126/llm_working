from django.contrib import admin
from .models import UserProfile, Skill, UserSkill, LearningResource, Recommendation, RecommendationSkill, RecommendationResource

# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'location', 'current_occupation', 'created_at')
    list_filter = ('created_at', 'location')
    search_fields = ('user__username', 'user__email', 'location', 'current_occupation')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'difficulty_level', 'is_active', 'created_at')
    list_filter = ('category', 'difficulty_level', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)

@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'skill', 'proficiency_level', 'years_experience', 'last_updated')
    list_filter = ('proficiency_level', 'skill__category', 'last_updated')
    search_fields = ('user_profile__user__username', 'skill__name')

@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'skill', 'difficulty_level', 'is_free', 'created_at')
    list_filter = ('resource_type', 'difficulty_level', 'is_free', 'skill__category', 'created_at')
    search_fields = ('title', 'description', 'url')
    list_editable = ('is_free',)

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'title', 'recommendation_type', 'generated_by_llm', 'is_active', 'created_at')
    list_filter = ('recommendation_type', 'generated_by_llm', 'is_active', 'created_at')
    search_fields = ('user_profile__user__username', 'title', 'description')
    list_editable = ('is_active',)

@admin.register(RecommendationSkill)
class RecommendationSkillAdmin(admin.ModelAdmin):
    list_display = ('recommendation', 'skill', 'priority')
    list_filter = ('recommendation__recommendation_type', 'skill__category')
    search_fields = ('recommendation__title', 'skill__name')
    list_editable = ('priority',)

@admin.register(RecommendationResource)
class RecommendationResourceAdmin(admin.ModelAdmin):
    list_display = ('recommendation', 'resource', 'relevance_score')
    list_filter = ('recommendation__recommendation_type', 'resource__resource_type')
    search_fields = ('recommendation__title', 'resource__title')