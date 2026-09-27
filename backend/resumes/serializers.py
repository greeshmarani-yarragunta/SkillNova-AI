from rest_framework import serializers
from .models import ResumeAnalysis


class ResumeAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeAnalysis
        fields = [
            'id', 'student', 'file_name', 'target_role',
            'detected_skills', 'missing_skills', 'match_percentage',
            'education_detected', 'projects_detected', 'experience_detected',
            'tools_detected', 'recommended_learning_path', 'created_at'
        ]
        read_only_fields = ['id', 'student', 'created_at']
