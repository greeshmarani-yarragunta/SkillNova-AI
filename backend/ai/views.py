from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count

from .models import AIChatMessage, InterviewSession, AIGeneratedQuestionBank
from .serializers import (
    AIChatMessageSerializer, InterviewSessionSerializer,
    AIGeneratedQuestionBankSerializer
)
from .service import ai_service
from accounts.models import Skill
from accounts.permissions import IsInstructor, IsAdmin, IsStudent
from notifications.models import Notification
from assessments.models import Assessment


class AIAskAssistantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question = request.data.get('question', '').strip()
        if not question:
            return Response({'error': 'Question cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve recent conversation context for this user
        recent_msgs = AIChatMessage.objects.filter(user=request.user).order_by('-created_at')[:6]
        conversation_context = "\n".join([
            f"{'Student' if m.role == 'user' else 'SkillNova AI'}: {m.message}"
            for m in reversed(list(recent_msgs))
        ])

        # Record student prompt
        AIChatMessage.objects.create(
            user=request.user,
            role='user',
            message=question
        )

        # Call AI service with context
        ai_resp = ai_service.ask_learning_assistant(question, context=conversation_context)

        # Record assistant answer
        assistant_msg = AIChatMessage.objects.create(
            user=request.user,
            role='assistant',
            message=ai_resp.get('explanation', ''),
            code_snippet=ai_resp.get('code_snippet', ''),
            key_points=ai_resp.get('key_points', []),
            practice_question=ai_resp.get('practice_question', {})
        )

        return Response(AIChatMessageSerializer(assistant_msg).data, status=status.HTTP_200_OK)


class AIChatHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AIChatMessageSerializer

    def get_queryset(self):
        return AIChatMessage.objects.filter(user=self.request.user).order_by('created_at')[:40]


class AIInterviewGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target_role = request.data.get('target_role', 'Python Full Stack Developer')
        experience_level = request.data.get('experience_level', 'Fresher')
        skills = request.data.get('skills', ['Python', 'Django', 'SQL', 'REST APIs'])

        questions = ai_service.generate_interview_questions(
            target_role=target_role,
            experience_level=experience_level,
            skills=skills
        )

        session = InterviewSession.objects.create(
            student=request.user,
            target_role=target_role,
            experience_level=experience_level,
            skills=skills,
            questions=questions
        )

        return Response(InterviewSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class AIInterviewSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        session = get_object_or_404(InterviewSession, id=pk, student=request.user)
        answers = request.data.get('answers', {})  # { question_id: answer_text }

        evaluation_data = ai_service.evaluate_interview_answers(
            target_role=session.target_role,
            questions=session.questions,
            answers=answers
        )

        session.answers = answers
        session.evaluation = evaluation_data.get('evaluations', [])
        session.overall_feedback = evaluation_data.get('overall_feedback', '')
        session.overall_score = evaluation_data.get('overall_score', 0.0)
        session.strengths = evaluation_data.get('strengths', [])
        session.improvements = evaluation_data.get('improvements', [])
        session.is_completed = True
        session.save()

        # Notify student
        Notification.objects.create(
            user=request.user,
            title="Interview Feedback Ready",
            message=f"Your AI mock interview for '{session.target_role}' has been analyzed. Score: {session.overall_score}%",
            notification_type='interview',
            link=f"/interview-prep"
        )

        return Response(InterviewSessionSerializer(session).data, status=status.HTTP_200_OK)


class AIInterviewHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InterviewSessionSerializer

    def get_queryset(self):
        return InterviewSession.objects.filter(student=self.request.user).order_by('-created_at')


class AIInterviewDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InterviewSessionSerializer

    def get_queryset(self):
        return InterviewSession.objects.filter(student=self.request.user)


class InstructorGenerateQuestionsView(APIView):
    permission_classes = [IsInstructor]

    def post(self, request):
        skill_id = request.data.get('skill_id')
        difficulty = request.data.get('difficulty', 'Intermediate')
        count = int(request.data.get('question_count', 5))
        topic = request.data.get('topic')

        skill = get_object_or_404(Skill, id=skill_id)

        generated = ai_service.instructor_generate_questions(
            skill_name=skill.name,
            difficulty=difficulty,
            count=count
        )

        created_objs = []
        for q in generated:
            item = AIGeneratedQuestionBank.objects.create(
                instructor=request.user,
                skill=skill,
                topic=topic or q.get('topic', 'General'),
                difficulty=difficulty,
                question_text=q.get('question_text', ''),
                option_a=q.get('option_a', ''),
                option_b=q.get('option_b', ''),
                option_c=q.get('option_c', ''),
                option_d=q.get('option_d', ''),
                correct_option=q.get('correct_option', 'A').upper(),
                explanation=q.get('explanation', ''),
                is_reviewed=False,
                is_published=False
            )
            created_objs.append(item)

        return Response(
            AIGeneratedQuestionBankSerializer(created_objs, many=True).data,
            status=status.HTTP_201_CREATED
        )


class InstructorDraftQuestionsView(APIView):
    permission_classes = [IsInstructor]

    def get(self, request, pk=None):
        if pk:
            question = get_object_or_404(AIGeneratedQuestionBank, id=pk)
            return Response(AIGeneratedQuestionBankSerializer(question).data)

        qs = AIGeneratedQuestionBank.objects.all().select_related('skill', 'instructor').order_by('-created_at')
        if not (request.user.role == 'ADMIN' or request.user.is_superuser):
            qs = qs.filter(instructor=request.user)

        skill_param = request.query_params.get('skill_id')
        if skill_param:
            qs = qs.filter(skill_id=skill_param)

        status_param = request.query_params.get('status')
        if status_param == 'approved':
            qs = qs.filter(is_published=True)
        elif status_param == 'draft':
            qs = qs.filter(is_published=False)

        difficulty_param = request.query_params.get('difficulty')
        if difficulty_param:
            qs = qs.filter(difficulty=difficulty_param)

        search_param = request.query_params.get('search')
        if search_param:
            qs = qs.filter(question_text__icontains=search_param)

        return Response(AIGeneratedQuestionBankSerializer(qs, many=True).data)

    def post(self, request, pk=None):
        # If pk provided, action is approve/publish
        if pk:
            question = get_object_or_404(AIGeneratedQuestionBank, id=pk)
            question.is_reviewed = True
            question.is_published = True
            question.save()
            return Response({
                'message': 'Question approved and added to active assessment pool.',
                'question': AIGeneratedQuestionBankSerializer(question).data
            }, status=status.HTTP_200_OK)

        # Otherwise, manual question creation by instructor
        skill_id = request.data.get('skill_id')
        if not skill_id:
            return Response({'error': 'skill_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        skill = get_object_or_404(Skill, id=skill_id)

        question = AIGeneratedQuestionBank.objects.create(
            instructor=request.user,
            skill=skill,
            topic=request.data.get('topic', 'General'),
            difficulty=request.data.get('difficulty', 'Intermediate'),
            question_text=request.data.get('question_text', ''),
            option_a=request.data.get('option_a', ''),
            option_b=request.data.get('option_b', ''),
            option_c=request.data.get('option_c', ''),
            option_d=request.data.get('option_d', ''),
            correct_option=request.data.get('correct_option', 'A').upper(),
            explanation=request.data.get('explanation', ''),
            is_reviewed=True,
            is_published=request.data.get('is_published', True)
        )
        return Response(AIGeneratedQuestionBankSerializer(question).data, status=status.HTTP_201_CREATED)

    def patch(self, request, pk=None):
        question = get_object_or_404(AIGeneratedQuestionBank, id=pk)
        if not (request.user.role == 'ADMIN' or request.user.is_superuser or question.instructor == request.user):
            raise permissions.PermissionDenied("You are not authorized to edit this question.")

        serializer = AIGeneratedQuestionBankSerializer(question, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(is_reviewed=True)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        question = get_object_or_404(AIGeneratedQuestionBank, id=pk)
        if not (request.user.role == 'ADMIN' or request.user.is_superuser or question.instructor == request.user):
            raise permissions.PermissionDenied("You are not authorized to delete this question.")
        question.delete()
        return Response({'message': 'Question deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class InstructorStatsView(APIView):
    permission_classes = [IsInstructor]

    def get(self, request):
        total_questions = AIGeneratedQuestionBank.objects.filter(instructor=request.user).count()
        total_assessments = Assessment.objects.count()
        active_skills = Skill.objects.count()
        student_attempts = Assessment.objects.filter(is_completed=True).count()
        avg_score = Assessment.objects.filter(is_completed=True).aggregate(Avg('percentage'))['percentage__avg'] or 0.0

        # Recent attempts
        recent_assessments = Assessment.objects.filter(is_completed=True).select_related('student', 'skill').order_by('-completed_at')[:8]
        recent_list = []
        for a in recent_assessments:
            recent_list.append({
                'id': a.id,
                'student_email': a.student.email,
                'skill_name': a.skill.name,
                'difficulty': a.difficulty,
                'percentage': a.percentage,
                'skill_level': a.skill_level,
                'completed_at': a.completed_at
            })

        return Response({
            'total_questions': total_questions,
            'total_assessments': total_assessments,
            'active_skills': active_skills,
            'student_attempts': student_attempts,
            'avg_score': round(avg_score, 1),
            'recent_attempts': recent_list
        })


class InstructorStudentPerformanceView(APIView):
    permission_classes = [IsInstructor]

    def get(self, request):
        assessments = Assessment.objects.filter(is_completed=True).select_related('student', 'skill').order_by('-completed_at')

        skill_filter = request.query_params.get('skill_id')
        if skill_filter:
            assessments = assessments.filter(skill_id=skill_filter)

        search = request.query_params.get('search')
        if search:
            assessments = assessments.filter(student__email__icontains=search)

        results = []
        for a in assessments[:50]:
            results.append({
                'id': a.id,
                'student_email': a.student.email,
                'student_role': getattr(a.student, 'student_profile', None).target_role if hasattr(a.student, 'student_profile') else 'Developer',
                'skill_name': a.skill.name,
                'difficulty': a.difficulty,
                'score': a.score,
                'percentage': a.percentage,
                'skill_level': a.skill_level,
                'strong_areas': a.strong_areas,
                'weak_areas': a.weak_areas,
                'completed_at': a.completed_at
            })

        return Response(results)
