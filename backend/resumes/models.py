from django.db import models
from django.conf import settings


class ResumeAnalysis(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resume_analyses'
    )
    file_name = models.CharField(max_length=255)
    target_role = models.CharField(max_length=150)
    raw_text = models.TextField(blank=True, default='')
    detected_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    match_percentage = models.FloatField(default=0.0)
    education_detected = models.JSONField(default=list)
    projects_detected = models.JSONField(default=list)
    experience_detected = models.JSONField(default=list)
    tools_detected = models.JSONField(default=list)
    recommended_learning_path = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.email} - Resume for {self.target_role} ({self.match_percentage}%)"
