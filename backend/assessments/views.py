from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Assessment, AssessmentQuestion, PersonalizedRoadmap
from .serializers import AssessmentSerializer, PersonalizedRoadmapSerializer
from accounts.models import Skill, StudentSkill
from ai.service import ai_service
from notifications.models import Notification


from accounts.permissions import IsAdmin, IsInstructor, CanViewAssessmentResult
from ai.models import AIGeneratedQuestionBank
from django.db.models import Q


class GenerateAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        skill_id = request.data.get('skill_id')
        difficulty = request.data.get('difficulty', 'Intermediate')

        # Backend strictly enforces exactly 30 questions regardless of frontend inputs
        REQUIRED_QUESTION_COUNT = 30

        if not skill_id:
            return Response({'error': 'skill_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        skill = get_object_or_404(Skill, id=skill_id)

        # Check approved question bank first (up to 30)
        bank_qs = list(AIGeneratedQuestionBank.objects.filter(
            skill=skill,
            is_published=True
        ).filter(Q(difficulty__iexact=difficulty) | Q(difficulty='Intermediate'))[:REQUIRED_QUESTION_COUNT])

        selected_questions = []
        for bq in bank_qs:
            selected_questions.append({
                'question_text': bq.question_text,
                'option_a': bq.option_a,
                'option_b': bq.option_b,
                'option_c': bq.option_c,
                'option_d': bq.option_d,
                'correct_option': bq.correct_option,
                'explanation': bq.explanation,
                'topic': bq.topic,
                'difficulty': bq.difficulty
            })

        needed = REQUIRED_QUESTION_COUNT - len(selected_questions)
        if needed > 0:
            ai_questions = ai_service.generate_assessment_questions(
                skill_name=skill.name,
                difficulty=difficulty,
                count=needed
            )
            if not isinstance(ai_questions, list):
                ai_questions = []

            # Filter valid questions
            valid_ai_qs = [
                q for q in ai_questions
                if isinstance(q, dict) and q.get('question_text') and q.get('option_a') and q.get('correct_option')
            ]
            selected_questions.extend(valid_ai_qs)

        # If AI generation returns more than 30: Keep exactly 30 valid questions
        if len(selected_questions) > REQUIRED_QUESTION_COUNT:
            selected_questions = selected_questions[:REQUIRED_QUESTION_COUNT]

        # If AI generation returns fewer than 30: Supplement with heuristic to reach exactly 30
        if len(selected_questions) < REQUIRED_QUESTION_COUNT:
            extra_needed = REQUIRED_QUESTION_COUNT - len(selected_questions)
            existing_texts = {q['question_text'] for q in selected_questions if isinstance(q, dict) and 'question_text' in q}
            fallback_qs = ai_service._heuristic_assessment_questions(
                skill_name=skill.name,
                difficulty=difficulty,
                count=extra_needed,
                exclude_texts=existing_texts
            )
            selected_questions.extend(fallback_qs)
            if len(selected_questions) > REQUIRED_QUESTION_COUNT:
                selected_questions = selected_questions[:REQUIRED_QUESTION_COUNT]

        # Strict validation: Assessment cannot start with fewer or more than 30 questions
        if len(selected_questions) != REQUIRED_QUESTION_COUNT:
            return Response(
                {
                    'error': f'Failed to generate the required {REQUIRED_QUESTION_COUNT} questions for this assessment. Received {len(selected_questions)} questions.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Create assessment record with question_count = 30
        assessment = Assessment.objects.create(
            student=request.user,
            skill=skill,
            difficulty=difficulty,
            question_count=REQUIRED_QUESTION_COUNT
        )

        # Bulk create exactly 30 questions
        questions_to_create = []
        for q in selected_questions:
            questions_to_create.append(
                AssessmentQuestion(
                    assessment=assessment,
                    question_text=q.get('question_text', ''),
                    option_a=q.get('option_a', ''),
                    option_b=q.get('option_b', ''),
                    option_c=q.get('option_c', ''),
                    option_d=q.get('option_d', ''),
                    correct_option=q.get('correct_option', 'A').upper(),
                    explanation=q.get('explanation', ''),
                    topic=q.get('topic', 'General'),
                    difficulty=q.get('difficulty', difficulty)
                )
            )
        AssessmentQuestion.objects.bulk_create(questions_to_create)

        # Validate database integrity: verify exactly 30 questions saved
        saved_count = assessment.questions.count()
        if saved_count != REQUIRED_QUESTION_COUNT:
            assessment.delete()
            return Response(
                {'error': f'Assessment database verification failed: expected {REQUIRED_QUESTION_COUNT} questions, but found {saved_count}.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            AssessmentSerializer(assessment).data,
            status=status.HTTP_201_CREATED
        )


class SubmitAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        assessment = get_object_or_404(Assessment, id=pk, student=request.user)
        if assessment.is_completed:
            return Response(
                AssessmentSerializer(assessment).data,
                status=status.HTTP_200_OK
            )

        REQUIRED_QUESTION_COUNT = 30
        questions = assessment.questions.all()

        # Backend validates assessment contains exactly 30 questions
        if questions.count() != REQUIRED_QUESTION_COUNT:
            return Response(
                {'error': f'Assessment must contain exactly {REQUIRED_QUESTION_COUNT} questions, but has {questions.count()}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_answers = request.data.get('answers', {})  # { question_id: 'A' }

        # Student cannot submit an incomplete assessment: all 30 must be answered
        unanswered = []
        for q in questions:
            chosen = user_answers.get(str(q.id)) or user_answers.get(q.id)
            if not chosen or str(chosen).strip().upper() not in ['A', 'B', 'C', 'D']:
                unanswered.append(q.id)

        if unanswered:
            return Response(
                {
                    'error': f'Incomplete assessment: All {REQUIRED_QUESTION_COUNT} questions must be answered before submitting. {len(unanswered)} question(s) remain unanswered.',
                    'unanswered_count': len(unanswered)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        results_for_ai = []
        for q in questions:
            chosen = str(user_answers.get(str(q.id)) or user_answers.get(q.id)).strip().upper()
            q.user_answer = chosen
            q.is_correct = (chosen == q.correct_option)
            q.save()

            results_for_ai.append({
                'topic': q.topic,
                'is_correct': q.is_correct,
                'question_text': q.question_text
            })

        # Run AI skill-level & gap analysis
        analysis = ai_service.analyze_assessment_results(
            skill_name=assessment.skill.name,
            difficulty=assessment.difficulty,
            question_results=results_for_ai
        )

        # Update Assessment
        assessment.question_count = REQUIRED_QUESTION_COUNT
        assessment.score = analysis['score']
        assessment.percentage = analysis['percentage']
        assessment.skill_level = analysis['skill_level']
        assessment.strong_areas = analysis['strong_areas']
        assessment.weak_areas = analysis['weak_areas']
        assessment.recommendations = analysis['recommendations']
        assessment.is_completed = True
        assessment.completed_at = timezone.now()
        assessment.save()

        # Update or create StudentSkill entry
        student_skill, _ = StudentSkill.objects.get_or_create(
            student=request.user,
            skill=assessment.skill
        )
        student_skill.proficiency_level = analysis['skill_level']
        student_skill.assessment_score = analysis['percentage']
        student_skill.progress_percentage = min(100, max(student_skill.progress_percentage, int(analysis['percentage'])))
        student_skill.last_assessed = timezone.now()
        student_skill.save()

        # Generate or update personalized roadmap
        roadmap_data = ai_service.generate_roadmap(
            skill_name=assessment.skill.name,
            skill_level=analysis['skill_level'],
            weak_topics=analysis['weak_areas'],
            target_role=getattr(request.user, 'student_profile', None).target_role if hasattr(request.user, 'student_profile') else 'Developer'
        )
        roadmap, _ = PersonalizedRoadmap.objects.update_or_create(
            student=request.user,
            skill=assessment.skill,
            defaults={
                'title': roadmap_data['title'],
                'stages': roadmap_data['stages']
            }
        )

        # Notify user
        Notification.objects.create(
            user=request.user,
            title=f"{assessment.skill.name} Assessment Completed",
            message=f"You scored {assessment.percentage}% ({assessment.skill_level} Level). Detailed skill analysis and AI recommendations are ready!",
            notification_type='assessment',
            link=f"/assessments/{assessment.id}"
        )

        return Response(
            AssessmentSerializer(assessment).data,
            status=status.HTTP_200_OK
        )


class AssessmentResultsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        return Assessment.objects.filter(student=self.request.user, is_completed=True).select_related('skill').order_by('-completed_at')


class AssessmentDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, CanViewAssessmentResult]
    serializer_class = AssessmentSerializer
    queryset = Assessment.objects.all().select_related('skill', 'student')


class PersonalizedRoadmapView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, skill_id):
        skill = get_object_or_404(Skill, id=skill_id)
        roadmap = PersonalizedRoadmap.objects.filter(student=request.user, skill=skill).first()

        if not roadmap:
            # Auto-generate baseline roadmap if user hasn't taken assessment yet
            target_role = request.user.student_profile.target_role if hasattr(request.user, 'student_profile') else 'Developer'
            data = ai_service.generate_roadmap(skill.name, 'Beginner', [], target_role)
            roadmap = PersonalizedRoadmap.objects.create(
                student=request.user,
                skill=skill,
                title=data['title'],
                stages=data['stages']
            )

        return Response(PersonalizedRoadmapSerializer(roadmap).data)

    def post(self, request, skill_id):
        skill = get_object_or_404(Skill, id=skill_id)
        target_role = request.user.student_profile.target_role if hasattr(request.user, 'student_profile') else 'Developer'
        last_assessment = Assessment.objects.filter(student=request.user, skill=skill, is_completed=True).first()

        weak_topics = last_assessment.weak_areas if last_assessment else []
        level = last_assessment.skill_level if last_assessment else 'Beginner'

        data = ai_service.generate_roadmap(skill.name, level, weak_topics, target_role)
        roadmap, _ = PersonalizedRoadmap.objects.update_or_create(
            student=request.user,
            skill=skill,
            defaults={
                'title': data['title'],
                'stages': data['stages']
            }
        )
        return Response(PersonalizedRoadmapSerializer(roadmap).data)


class AdminAssessmentManagementView(generics.ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        qs = Assessment.objects.all().select_related('student', 'skill').order_by('-created_at')
        skill = self.request.query_params.get('skill_id')
        if skill:
            qs = qs.filter(skill_id=skill)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(student__email__icontains=search)
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            qs = qs.filter(difficulty__iexact=difficulty)
        return qs
