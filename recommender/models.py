from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    INTEREST_DOMAINS = [
        ('web_dev', 'Full-Stack Web Development'),
        ('ai_ml', 'AI & Machine Learning'),
        ('data_science', 'Data Science & Analytics'),
        ('cloud_devops', 'Cloud & DevOps Engineering'),
        ('cybersecurity', 'Cybersecurity & Ethical Hacking'),
        ('ui_ux', 'UI/UX & Product Design'),
        ('product_management', 'Product & Agile Leadership'),
        ('soft_skills', 'Executive Communication & Soft Skills'),
    ]

    EXPERIENCE_LEVELS = [
        ('beginner', 'Beginner (0-1 yrs)'),
        ('intermediate', 'Intermediate (1-3 yrs)'),
        ('advanced', 'Advanced (3+ yrs)'),
        ('career_switcher', 'Career Switcher'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    education_level = models.CharField(max_length=100, blank=True)
    current_occupation = models.CharField(max_length=100, blank=True)
    target_role = models.CharField(max_length=100, blank=True, default='Full-Stack Web Developer')
    primary_interest = models.CharField(max_length=50, choices=INTEREST_DOMAINS, default='web_dev')
    interests = models.TextField(blank=True, help_text="Comma-separated or descriptive interests")
    goals = models.TextField(blank=True, help_text="Career aspirations and goals")
    weekly_hours = models.IntegerField(default=10, help_text="Hours available per week for learning")
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='beginner')
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

    DOMAIN_CHOICES = [
        ('web_dev', 'Full-Stack Web Development'),
        ('ai_ml', 'AI & Machine Learning'),
        ('data_science', 'Data Science & Analytics'),
        ('cloud_devops', 'Cloud & DevOps Engineering'),
        ('cybersecurity', 'Cybersecurity & Ethical Hacking'),
        ('ui_ux', 'UI/UX & Product Design'),
        ('product_management', 'Product & Agile Leadership'),
        ('soft_skills', 'Executive Communication & Soft Skills'),
        ('general', 'General Core Skills'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='technical')
    domain = models.CharField(max_length=50, choices=DOMAIN_CHOICES, default='web_dev')
    description = models.TextField()
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='beginner')
    icon = models.CharField(max_length=60, default='fas fa-code', help_text="FontAwesome icon class")
    market_demand = models.CharField(max_length=20, default='High', choices=[
        ('Very High', 'Very High'),
        ('High', 'High'),
        ('Medium', 'Medium'),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['domain', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_domain_display()})"


class UserSkill(models.Model):
    PROFICIENCY_LEVELS = [
        ('none', 'None'),
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='user_skills')
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS, default='none')
    years_experience = models.FloatField(null=True, blank=True)
    confidence_score = models.IntegerField(default=50, help_text="1 to 100 confidence scale")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user_profile', 'skill')
        ordering = ['-last_updated']

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.skill.name} ({self.proficiency_level})"

    @property
    def numeric_score(self):
        mapping = {'none': 0, 'basic': 25, 'intermediate': 50, 'advanced': 75, 'expert': 100}
        return mapping.get(self.proficiency_level, 0)


class AssessmentQuestion(models.Model):
    domain = models.CharField(max_length=50, choices=Skill.DOMAIN_CHOICES)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, null=True, blank=True, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_option = models.CharField(max_length=1, choices=[
        ('a', 'Option A'),
        ('b', 'Option B'),
        ('c', 'Option C'),
        ('d', 'Option D'),
    ])
    explanation = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='intermediate')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.domain}] {self.question_text[:60]}..."


class AssessmentResult(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='assessments')
    domain = models.CharField(max_length=50)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    score_percentage = models.FloatField(default=0.0)
    assessed_level = models.CharField(max_length=30, default='Beginner')
    feedback_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.domain} ({self.score_percentage:.1f}%)"


class LearningResource(models.Model):
    RESOURCE_TYPES = [
        ('course', 'Course'),
        ('tutorial', 'Tutorial'),
        ('article', 'Article'),
        ('video', 'Video'),
        ('book', 'Book'),
        ('project', 'Hands-on Project'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    url = models.URLField()
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='resources')
    provider = models.CharField(max_length=100, default='Open Source / Web')
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='beginner')
    rating = models.FloatField(null=True, blank=True, default=4.8)
    duration_hours = models.FloatField(null=True, blank=True, default=12.0)
    cost = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_free = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rating', 'title']

    def __str__(self):
        return self.title


class Recommendation(models.Model):
    RECOMMENDATION_TYPES = [
        ('realtime_roadmap', 'Real-Time Career Roadmap'),
        ('skill_gap', 'Skill Gap Analysis'),
        ('learning_path', 'Learning Path'),
        ('career_advice', 'Career Advice'),
    ]

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='recommendations')
    recommendation_type = models.CharField(max_length=30, choices=RECOMMENDATION_TYPES, default='realtime_roadmap')
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_role = models.CharField(max_length=100, blank=True)
    match_score = models.FloatField(default=70.0, help_text="Market readiness match score (0-100%)")
    generated_by_llm = models.BooleanField(default=True)
    groq_model_used = models.CharField(max_length=60, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.title}"


class RecommendationSkill(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Mastered'),
    ]

    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='recommendation_skills')
    priority = models.IntegerField(default=1)  # 1 = highest priority
    timeline = models.CharField(max_length=60, default='Month 1')
    reasoning = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return f"{self.recommendation.title} - {self.skill.name} (P{self.priority})"


class RecommendationResource(models.Model):
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE, related_name='resources')
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE, related_name='recommendation_resources')
    relevance_score = models.FloatField(default=0.9)

    class Meta:
        ordering = ['-relevance_score']

    def __str__(self):
        return f"{self.recommendation.title} - {self.resource.title}"