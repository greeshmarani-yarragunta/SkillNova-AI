from rest_framework import serializers
from .models import AIChatMessage, InterviewSession, AIGeneratedQuestionBank
from accounts.serializers import SkillSerializer


class AIChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatMessage
        fields = ['id', 'user', 'role', 'message', 'code_snippet', 'key_points', 'practice_question', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class InterviewSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewSession
        fields = [
            'id', 'student', 'target_role', 'experience_level', 'skills',
            'questions', 'answers', 'evaluation', 'overall_feedback',
            'overall_score', 'strengths', 'improvements', 'is_completed', 'created_at'
        ]
        read_only_fields = ['id', 'student', 'is_completed', 'created_at']


class AIGeneratedQuestionBankSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = AIGeneratedQuestionBank
        fields = [
            'id', 'instructor', 'skill', 'skill_name', 'topic', 'difficulty',
            'question_text', 'option_a', 'option_b', 'option_c', 'option_d',
            'correct_option', 'explanation', 'is_reviewed', 'is_published',
            'created_at'
        ]
        read_only_fields = ['id', 'instructor', 'created_at']
