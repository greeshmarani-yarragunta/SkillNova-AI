from rest_framework import serializers
from .models import Assessment, AssessmentQuestion, PersonalizedRoadmap
from accounts.serializers import SkillSerializer


class AssessmentQuestionStudentSerializer(serializers.ModelSerializer):
    """Safe serializer for taking the assessment - hides answer until submitted"""
    class Meta:
        model = AssessmentQuestion
        fields = [
            'id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d',
            'topic', 'difficulty'
        ]


class AssessmentQuestionReviewSerializer(serializers.ModelSerializer):
    """Full serializer showing question, user answer, correct option, explanation"""
    class Meta:
        model = AssessmentQuestion
        fields = [
            'id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d',
            'correct_option', 'explanation', 'topic', 'difficulty', 'user_answer', 'is_correct'
        ]


class AssessmentSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_icon = serializers.CharField(source='skill.icon', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    student_name = serializers.SerializerMethodField()
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = [
            'id', 'student', 'student_email', 'student_name', 'skill', 'skill_name', 'skill_icon',
            'difficulty', 'question_count', 'score', 'percentage',
            'skill_level', 'strong_areas', 'weak_areas', 'recommendations',
            'is_completed', 'completed_at', 'created_at', 'questions'
        ]
        read_only_fields = ['id', 'student', 'score', 'percentage', 'skill_level', 'is_completed', 'completed_at', 'created_at']

    def get_student_name(self, obj):
        if obj.student:
            full_name = f"{obj.student.first_name} {obj.student.last_name}".strip()
            return full_name or obj.student.username or obj.student.email
        return ""

    def get_questions(self, obj):
        if obj.is_completed:
            return AssessmentQuestionReviewSerializer(obj.questions.all(), many=True).data
        return AssessmentQuestionStudentSerializer(obj.questions.all(), many=True).data


class PersonalizedRoadmapSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = PersonalizedRoadmap
        fields = ['id', 'student', 'skill', 'skill_name', 'title', 'stages', 'generated_at', 'updated_at']
        read_only_fields = ['id', 'student', 'generated_at', 'updated_at']
