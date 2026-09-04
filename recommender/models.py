from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    education_level = models.CharField(max_length=50, blank=True)
    current_occupation = models.CharField(max_length=100, blank=True)
    interests = models.TextField(blank=True)
    goals = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('soft', 'Soft Skills'),
        ('leadership', 'Leadership'),
        ('creative', 'Creative'),
        ('business', 'Business'),
        ('language', 'Language'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='beginner')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class UserSkill(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level = models.CharField(max_length=20, choices=[
        ('none', 'None'),
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ], default='none')
    years_experience = models.FloatField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user_profile', 'skill')

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.skill.name} ({self.proficiency_level})"

class LearningResource(models.Model):
    RESOURCE_TYPES = [
        ('course', 'Course'),
        ('tutorial', 'Tutorial'),
        ('article', 'Article'),
        ('video', 'Video'),
        ('book', 'Book'),
        ('podcast', 'Podcast'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    url = models.URLField()
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ])
    rating = models.FloatField(null=True, blank=True)
    duration_hours = models.FloatField(null=True, blank=True)
    cost = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_free = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Recommendation(models.Model):
    RECOMMENDATION_TYPES = [
        ('skill_gap', 'Skill Gap Analysis'),
        ('learning_path', 'Learning Path'),
        ('career_advice', 'Career Advice'),
    ]

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    generated_by_llm = models.BooleanField(default=True)
    groq_model_used = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.title}"

class RecommendationSkill(models.Model):
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    priority = models.IntegerField(default=1)  # 1 = highest priority
    reasoning = models.TextField(blank=True)

    def __str__(self):
        return f"{self.recommendation.title} - {self.skill.name}"

class RecommendationResource(models.Model):
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE)
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)
    relevance_score = models.FloatField(default=0.0)  # 0.0 to 1.0

    def __str__(self):
        return f"{self.recommendation.title} - {self.resource.title}"