from django.db import models
from django.conf import settings
from accounts.models import Skill


class Assessment(models.Model):
    DIFFICULTY_CHOICES = (
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    )

    LEVEL_CHOICES = (
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    difficulty = models.CharField(max_length=30, choices=DIFFICULTY_CHOICES, default='Intermediate')
    question_count = models.PositiveIntegerField(default=30)
    score = models.FloatField(default=0.0)
    percentage = models.FloatField(default=0.0)
    skill_level = models.CharField(max_length=30, choices=LEVEL_CHOICES, default='Beginner')
    strong_areas = models.JSONField(default=list, help_text="List of topics mastered")
    weak_areas = models.JSONField(default=list, help_text="List of topics needing improvement")
    recommendations = models.JSONField(default=list, help_text="List of actionable recommendations")
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.email} - {self.skill.name} Assessment ({self.percentage}%)"


class AssessmentQuestion(models.Model):
    OPTION_CHOICES = (
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    )

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    explanation = models.TextField(blank=True, default='')
    topic = models.CharField(max_length=100, default='Core')
    difficulty = models.CharField(max_length=30, default='Intermediate')
    user_answer = models.CharField(max_length=1, blank=True, null=True)
    is_correct = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"{self.assessment.skill.name} Q: {self.question_text[:50]}"


class PersonalizedRoadmap(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='roadmaps'
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='roadmaps')
    title = models.CharField(max_length=200)
    stages = models.JSONField(
        default=list,
        help_text="List of roadmap nodes: [{id, title, status: 'completed'|'current'|'recommended'|'locked', topics, description}]"
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'skill')

    def __str__(self):
        return f"Roadmap for {self.student.email}: {self.title}"
