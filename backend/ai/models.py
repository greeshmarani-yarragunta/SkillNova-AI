from django.db import models
from django.conf import settings
from accounts.models import Skill


class AIChatMessage(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'SkillNova AI Assistant'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_chats'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    message = models.TextField()
    code_snippet = models.TextField(blank=True, default='')
    key_points = models.JSONField(default=list, blank=True)
    practice_question = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.email} - {self.role}: {self.message[:40]}"


class InterviewSession(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interviews'
    )
    target_role = models.CharField(max_length=150)
    experience_level = models.CharField(max_length=50, default='Fresher')
    skills = models.JSONField(default=list)
    questions = models.JSONField(
        default=list,
        help_text="Generated questions: [{id, category: technical|conceptual|scenario|project|hr, question, expected_concepts}]"
    )
    answers = models.JSONField(
        default=dict,
        help_text="Student answers: {question_id: answer_text}"
    )
    evaluation = models.JSONField(
        default=list,
        help_text="Evaluation per question: [{question_id, score, feedback, missing_concepts, tips}]"
    )
    overall_feedback = models.TextField(blank=True, default='')
    overall_score = models.FloatField(default=0.0)
    strengths = models.JSONField(default=list)
    improvements = models.JSONField(default=list)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.email} - Interview for {self.target_role} ({self.overall_score}%)"


class AIGeneratedQuestionBank(models.Model):
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_questions'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='generated_questions'
    )
    topic = models.CharField(max_length=120, default='General')
    difficulty = models.CharField(max_length=30, default='Intermediate')
    question_text = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_option = models.CharField(max_length=1)
    explanation = models.TextField(blank=True, default='')
    is_reviewed = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"AI Q [{self.skill.name}]: {self.question_text[:50]}"
