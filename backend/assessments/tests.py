from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User, Skill, StudentProfile
from assessments.models import Assessment
from ai.models import AIGeneratedQuestionBank
from ai.service import ai_service


class AssessmentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            username='stud_assess', email='stud_assess@test.com', password='Password123', role='STUDENT'
        )
        self.other_student = User.objects.create_user(
            username='stud_other', email='stud_other@test.com', password='Password123', role='STUDENT'
        )
        self.instructor = User.objects.create_user(
            username='inst_assess', email='inst_assess@test.com', password='Password123', role='INSTRUCTOR'
        )
        self.admin = User.objects.create_user(
            username='admin_assess', email='admin_assess@test.com', password='Password123', role='ADMIN', is_superuser=True
        )
        StudentProfile.objects.create(user=self.student, target_role='Python Engineer')
        self.skill = Skill.objects.create(name='Python', slug='python', description='Core Python programming')
        self.completed_assessment = Assessment.objects.create(
            student=self.student,
            skill=self.skill,
            difficulty='Intermediate',
            question_count=30,
            score=24.0,
            percentage=80.0,
            skill_level='Intermediate',
            strong_areas=['OOP', 'Functions'],
            weak_areas=['Generators'],
            recommendations=['Practice generators and iterators'],
            is_completed=True
        )

    def test_new_assessment_contains_exactly_30_questions(self):
        """1. Verify new assessment contains exactly 30 questions."""
        self.client.force_authenticate(user=self.student)
        gen_url = reverse('assessment_generate')
        res_gen = self.client.post(gen_url, {
            'skill_id': self.skill.id,
            'difficulty': 'Intermediate'
        })
        self.assertEqual(res_gen.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_gen.data['question_count'], 30)
        questions = res_gen.data['questions']
        self.assertEqual(len(questions), 30)

        # Database verification
        assessment = Assessment.objects.get(id=res_gen.data['id'])
        self.assertEqual(assessment.questions.count(), 30)
        self.assertEqual(assessment.question_count, 30)

    def test_backend_enforces_30_questions_even_if_other_number_sent(self):
        """6. Backend enforces the 30-question requirement even if client sends 5, 10, or 15."""
        self.client.force_authenticate(user=self.student)
        gen_url = reverse('assessment_generate')

        for requested_count in [5, 10, 15, 100]:
            res = self.client.post(gen_url, {
                'skill_id': self.skill.id,
                'difficulty': 'Intermediate',
                'question_count': requested_count
            })
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            self.assertEqual(res.data['question_count'], 30)
            self.assertEqual(len(res.data['questions']), 30)

    def test_student_cannot_submit_incomplete_assessment(self):
        """3. Student cannot submit an incomplete assessment."""
        self.client.force_authenticate(user=self.student)
        gen_url = reverse('assessment_generate')
        res_gen = self.client.post(gen_url, {
            'skill_id': self.skill.id,
            'difficulty': 'Intermediate'
        })
        self.assertEqual(res_gen.status_code, status.HTTP_201_CREATED)
        assessment_id = res_gen.data['id']
        questions = res_gen.data['questions']
        self.assertEqual(len(questions), 30)

        sub_url = reverse('assessment_submit', kwargs={'pk': assessment_id})

        # Attempt submitting only 10 answers out of 30
        partial_answers = {str(q['id']): 'A' for q in questions[:10]}
        res_sub_incomplete = self.client.post(sub_url, {'answers': partial_answers}, format='json')
        self.assertEqual(res_sub_incomplete.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Incomplete assessment', res_sub_incomplete.data['error'])
        self.assertEqual(res_sub_incomplete.data['unanswered_count'], 20)

        # Assessment remains incomplete in database
        assessment = Assessment.objects.get(id=assessment_id)
        self.assertFalse(assessment.is_completed)

    def test_score_calculation_works_correctly_for_30_questions(self):
        """4. Score calculation works correctly for 30 questions."""
        self.client.force_authenticate(user=self.student)
        gen_url = reverse('assessment_generate')
        res_gen = self.client.post(gen_url, {
            'skill_id': self.skill.id,
            'difficulty': 'Intermediate'
        })
        self.assertEqual(res_gen.status_code, status.HTTP_201_CREATED)
        assessment_id = res_gen.data['id']
        assessment = Assessment.objects.get(id=assessment_id)
        db_questions = list(assessment.questions.all())
        self.assertEqual(len(db_questions), 30)

        # Build answers: exactly 23 correct and 7 incorrect
        answers = {}
        for idx, q in enumerate(db_questions):
            if idx < 23:
                answers[str(q.id)] = q.correct_option  # Correct
            else:
                wrong_opt = 'B' if q.correct_option == 'A' else 'A'
                answers[str(q.id)] = wrong_opt  # Incorrect

        sub_url = reverse('assessment_submit', kwargs={'pk': assessment_id})
        res_sub = self.client.post(sub_url, {'answers': answers}, format='json')
        self.assertEqual(res_sub.status_code, status.HTTP_200_OK)
        self.assertTrue(res_sub.data['is_completed'])
        self.assertEqual(res_sub.data['question_count'], 30)
        self.assertEqual(res_sub.data['score'], 23)
        expected_percentage = round((23 / 30) * 100, 1)  # 76.7%
        self.assertEqual(res_sub.data['percentage'], expected_percentage)
        self.assertEqual(res_sub.data['skill_level'], 'Intermediate')
        self.assertIn('strong_areas', res_sub.data)
        self.assertIn('weak_areas', res_sub.data)
        self.assertIn('recommendations', res_sub.data)

    def test_ai_generated_assessment_contains_exactly_30_valid_questions(self):
        """5. AI-generated assessment contains exactly 30 valid questions."""
        # Test for Python skill
        py_questions = ai_service.generate_assessment_questions(skill_name='Python', difficulty='Intermediate')
        self.assertEqual(len(py_questions), 30)
        for q in py_questions:
            self.assertIn('question_text', q)
            self.assertIn('option_a', q)
            self.assertIn('option_b', q)
            self.assertIn('option_c', q)
            self.assertIn('option_d', q)
            self.assertIn(q['correct_option'], ['A', 'B', 'C', 'D'])
            self.assertIn('topic', q)
            self.assertIn('explanation', q)

        # Test for dynamic custom skill (e.g. AWS)
        aws_questions = ai_service.generate_assessment_questions(skill_name='AWS', difficulty='Advanced')
        self.assertEqual(len(aws_questions), 30)
        for q in aws_questions:
            self.assertIn('AWS', q['question_text'])
            self.assertIn(q['correct_option'], ['A', 'B', 'C', 'D'])

    def test_question_bank_integration(self):
        """Verify published question bank questions integrate seamlessly up to 30."""
        AIGeneratedQuestionBank.objects.create(
            instructor=self.admin,
            skill=self.skill,
            topic='Functions',
            difficulty='Intermediate',
            question_text='Bank Question: What is lambda in Python?',
            option_a='Anonymous function',
            option_b='Loop',
            option_c='Class',
            option_d='Module',
            correct_option='A',
            is_reviewed=True,
            is_published=True
        )

        self.client.force_authenticate(user=self.student)
        gen_url = reverse('assessment_generate')
        res_gen = self.client.post(gen_url, {
            'skill_id': self.skill.id,
            'difficulty': 'Intermediate'
        })
        self.assertEqual(res_gen.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(res_gen.data['questions']), 30)
        q_texts = [q['question_text'] for q in res_gen.data['questions']]
        self.assertTrue(any('Bank Question' in t for t in q_texts))

    def test_admin_assessment_management_access(self):
        # Student cannot access admin assessments endpoint
        self.client.force_authenticate(user=self.student)
        admin_assess_url = reverse('admin_assessments')
        res = self.client.get(admin_assess_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Admin can access
        self.client.force_authenticate(user=self.admin)
        res_admin = self.client.get(admin_assess_url)
        self.assertEqual(res_admin.status_code, status.HTTP_200_OK)

    def test_student_can_access_own_result(self):
        """Student can view their own assessment result."""
        self.client.force_authenticate(user=self.student)
        url = reverse('assessment_detail', kwargs={'pk': self.completed_assessment.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], self.completed_assessment.id)
        self.assertEqual(res.data['student_email'], self.student.email)
        self.assertEqual(res.data['percentage'], 80.0)

    def test_student_cannot_access_another_students_result(self):
        """Student cannot access another student's assessment result (returns 403)."""
        self.client.force_authenticate(user=self.other_student)
        url = reverse('assessment_detail', kwargs={'pk': self.completed_assessment.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_can_access_authorized_student_results(self):
        """Instructor can access student assessment results."""
        self.client.force_authenticate(user=self.instructor)
        url = reverse('assessment_detail', kwargs={'pk': self.completed_assessment.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], self.completed_assessment.id)
        self.assertEqual(res.data['student_email'], self.student.email)
        self.assertEqual(res.data['score'], 24.0)

    def test_instructor_cannot_perform_unauthorized_admin_actions(self):
        """Instructor cannot perform unauthorized admin actions."""
        self.client.force_authenticate(user=self.instructor)
        admin_assess_url = reverse('admin_assessments')
        res = self.client.get(admin_assess_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_results(self):
        """Admin can access any student assessment result."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('assessment_detail', kwargs={'pk': self.completed_assessment.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], self.completed_assessment.id)

    def test_nonexistent_assessment_returns_404(self):
        """Nonexistent assessment returns 404 Not Found."""
        self.client.force_authenticate(user=self.instructor)
        url = reverse('assessment_detail', kwargs={'pk': 999999})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_request_returns_401(self):
        """Unauthenticated request returns 401 Unauthorized."""
        # Unauthenticated client
        client = APIClient()
        url = reverse('assessment_detail', kwargs={'pk': self.completed_assessment.id})
        res = client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

