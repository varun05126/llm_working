from mongoengine import Document, EmbeddedDocument, fields
from django.contrib.auth.models import User
import datetime

class UserProfile(Document):
    user = fields.ReferenceField(User, unique=True)
    age = fields.IntField(null=True, blank=True)
    location = fields.StringField(max_length=100, blank=True)
    education_level = fields.StringField(max_length=50, blank=True)
    current_occupation = fields.StringField(max_length=100, blank=True)
    interests = fields.StringField(blank=True)
    goals = fields.StringField(blank=True)
    created_at = fields.DateTimeField(default=datetime.datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()
        return super(UserProfile, self).save(*args, **kwargs)

class Skill(Document):
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('soft', 'Soft Skills'),
        ('leadership', 'Leadership'),
        ('creative', 'Creative'),
        ('business', 'Business'),
        ('language', 'Language'),
        ('other', 'Other'),
    ]

    name = fields.StringField(max_length=100, unique=True)
    category = fields.StringField(max_length=20, choices=CATEGORY_CHOICES)
    description = fields.StringField()
    difficulty_level = fields.StringField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='beginner')
    is_active = fields.BooleanField(default=True)
    created_at = fields.DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.utcnow()
        return super(Skill, self).save(*args, **kwargs)

class UserSkill(Document):
    user_profile = fields.ReferenceField(UserProfile)
    skill = fields.ReferenceField(Skill)
    proficiency_level = fields.StringField(max_length=20, choices=[
        ('none', 'None'),
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ], default='none')
    years_experience = fields.FloatField(null=True, blank=True)
    last_updated = fields.DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'indexes': [
            {'fields': ['user_profile', 'skill'], 'unique': True}
        ]
    }

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.skill.name} ({self.proficiency_level})"

    def save(self, *args, **kwargs):
        self.last_updated = datetime.datetime.utcnow()
        return super(UserSkill, self).save(*args, **kwargs)

class LearningResource(Document):
    RESOURCE_TYPES = [
        ('course', 'Course'),
        ('tutorial', 'Tutorial'),
        ('article', 'Article'),
        ('video', 'Video'),
        ('book', 'Book'),
        ('podcast', 'Podcast'),
    ]

    title = fields.StringField(max_length=200)
    description = fields.StringField()
    resource_type = fields.StringField(max_length=20, choices=RESOURCE_TYPES)
    url = fields.URLField()
    skill = fields.ReferenceField(Skill)
    difficulty_level = fields.StringField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ])
    rating = fields.FloatField(null=True, blank=True)
    duration_hours = fields.FloatField(null=True, blank=True)
    cost = fields.FloatField(null=True, blank=True)  # Using FloatField instead of DecimalField for simplicity
    is_free = fields.BooleanField(default=True)
    created_at = fields.DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.utcnow()
        return super(LearningResource, self).save(*args, **kwargs)

class Recommendation(Document):
    RECOMMENDATION_TYPES = [
        ('skill_gap', 'Skill Gap Analysis'),
        ('learning_path', 'Learning Path'),
        ('career_advice', 'Career Advice'),
    ]

    user_profile = fields.ReferenceField(UserProfile)
    recommendation_type = fields.StringField(max_length=20, choices=RECOMMENDATION_TYPES)
    title = fields.StringField(max_length=200)
    description = fields.StringField()
    generated_by_llm = fields.BooleanField(default=True)
    groq_model_used = fields.StringField(max_length=50, blank=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DateTimeField(default=datetime.datetime.utcnow)
    expires_at = fields.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.utcnow()
        return super(Recommendation, self).save(*args, **kwargs)

class RecommendationSkill(Document):
    recommendation = fields.ReferenceField(Recommendation)
    skill = fields.ReferenceField(Skill)
    priority = fields.IntField(default=1)  # 1 = highest priority
    reasoning = fields.StringField(blank=True)

    def __str__(self):
        return f"{self.recommendation.title} - {self.skill.name}"

class RecommendationResource(Document):
    recommendation = fields.ReferenceField(Recommendation)
    resource = fields.ReferenceField(LearningResource)
    relevance_score = fields.FloatField(default=0.0)  # 0.0 to 1.0

    def __str__(self):
        return f"{self.recommendation.title} - {self.resource.title}"