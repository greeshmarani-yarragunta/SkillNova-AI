from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User, Skill, StudentProfile
from ai.models import AIGeneratedQuestionBank, InterviewSession


class AIServiceAndInstructorTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            username='stud_ai', email='stud_ai@test.com', password='Password123', role='STUDENT'
        )
        StudentProfile.objects.create(user=self.student, target_role='Python Developer')

        self.instructor = User.objects.create_user(
            username='inst_ai', email='inst_ai@test.com', password='Password123', role='INSTRUCTOR'
        )
        self.skill = Skill.objects.create(name='Python', slug='python', description='Core Python programming')

    def test_ai_learning_assistant_python(self):
        self.client.force_authenticate(user=self.student)
        ask_url = reverse('ai_ask')
        res = self.client.post(ask_url, {'question': 'Explain Python inheritance'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('message', res.data)
        self.assertIn('inheritance', res.data['message'].lower())
        self.assertIn('super()', res.data['code_snippet'])

    def test_ai_learning_assistant_react_no_python_fallback(self):
        self.client.force_authenticate(user=self.student)
        ask_url = reverse('ai_ask')
        res = self.client.post(ask_url, {'question': 'What is React useEffect?'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        resp_text = (
            res.data.get('message', '') + ' ' +
            res.data.get('code_snippet', '') + ' ' +
            ' '.join(res.data.get('key_points', [])) + ' ' +
            str(res.data.get('practice_question', {}))
        ).lower()

        # Must contain React useEffect concepts
        self.assertIn('useeffect', resp_text)
        self.assertIn('hook', resp_text)
        self.assertIn('side effect', resp_text)
        self.assertIn('dependency array', resp_text)

        # Must NOT contain old generic Python template
        self.assertNotIn('solve_problem', resp_text)
        self.assertNotIn('pep 8', resp_text)
        self.assertNotIn('python dictionary', resp_text)
        self.assertNotIn('time complexity of searching by key', resp_text)

    def test_ai_learning_assistant_sql_no_python_fallback(self):
        self.client.force_authenticate(user=self.student)
        ask_url = reverse('ai_ask')
        res = self.client.post(ask_url, {'question': 'What is a SQL JOIN?'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        resp_text = (
            res.data.get('message', '') + ' ' +
            res.data.get('code_snippet', '') + ' ' +
            ' '.join(res.data.get('key_points', [])) + ' ' +
            str(res.data.get('practice_question', {}))
        ).lower()

        self.assertIn('join', resp_text)
        self.assertIn('table', resp_text)
        self.assertNotIn('python', resp_text)
        self.assertNotIn('solve_problem', resp_text)
        self.assertNotIn('pep 8', resp_text)

    def test_ai_learning_assistant_conversation_context(self):
        self.client.force_authenticate(user=self.student)
        ask_url = reverse('ai_ask')

        # First question
        res1 = self.client.post(ask_url, {'question': 'What is React useEffect?'}, format='json')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        # Follow-up question with pronoun "it"
        res2 = self.client.post(ask_url, {'question': 'Why do we need it?'}, format='json')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)

        resp2_text = (
            res2.data.get('message', '') + ' ' +
            res2.data.get('code_snippet', '') + ' ' +
            ' '.join(res2.data.get('key_points', [])) + ' ' +
            str(res2.data.get('practice_question', {}))
        ).lower()

        # Follow up must resolve "it" to React useEffect
        self.assertIn('useeffect', resp2_text)
        self.assertIn('react', resp2_text)
        self.assertNotIn('solve_problem', resp2_text)
        self.assertNotIn('pep 8', resp2_text)

    def test_ai_interview_workflow(self):
        self.client.force_authenticate(user=self.student)
        gen_url = reverse('ai_interview_generate')
        res_gen = self.client.post(gen_url, {
            'target_role': 'Python Developer',
            'experience_level': 'Fresher',
            'skills': ['Python', 'SQL']
        }, format='json')
        self.assertEqual(res_gen.status_code, status.HTTP_201_CREATED)
        session_id = res_gen.data['id']
        questions = res_gen.data['questions']
        self.assertTrue(len(questions) > 0)

        # Submit answers
        sub_url = reverse('ai_interview_submit', kwargs={'pk': session_id})
        answers = {str(q['id']): 'This is my technical answer covering basic principles.' for q in questions}
        res_sub = self.client.post(sub_url, {'answers': answers}, format='json')
        self.assertEqual(res_sub.status_code, status.HTTP_200_OK)
        self.assertTrue(res_sub.data['is_completed'])
        self.assertIn('overall_score', res_sub.data)
        self.assertIn('overall_feedback', res_sub.data)

    def test_instructor_question_bank_crud_and_approve(self):
        self.client.force_authenticate(user=self.instructor)

        # 1. AI question generation by instructor
        gen_url = reverse('ai_instructor_generate')
        res_gen = self.client.post(gen_url, {
            'skill_id': self.skill.id,
            'difficulty': 'Intermediate',
            'question_count': 3
        }, format='json')
        self.assertEqual(res_gen.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(res_gen.data), 3)
        draft_id = res_gen.data[0]['id']

        # 2. List instructor questions
        list_url = reverse('ai_instructor_drafts')
        res_list = self.client.get(list_url)
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res_list.data), 3)

        # 3. Approve draft question
        approve_url = reverse('ai_instructor_approve', kwargs={'pk': draft_id})
        res_app = self.client.post(approve_url)
        self.assertEqual(res_app.status_code, status.HTTP_200_OK)
        question_obj = AIGeneratedQuestionBank.objects.get(id=draft_id)
        self.assertTrue(question_obj.is_reviewed)
        self.assertTrue(question_obj.is_published)

        # 4. Manual question creation by instructor
        res_manual = self.client.post(list_url, {
            'skill_id': self.skill.id,
            'topic': 'Decorators',
            'difficulty': 'Advanced',
            'question_text': 'What does functools.wraps do?',
            'option_a': 'Preserves original metadata',
            'option_b': 'Increases execution speed',
            'option_c': 'Compiles to C',
            'option_d': 'None of the above',
            'correct_option': 'A',
            'explanation': 'It copies docstring and function name.'
        }, format='json')
        self.assertEqual(res_manual.status_code, status.HTTP_201_CREATED)

    def test_student_cannot_access_instructor_endpoints(self):
        self.client.force_authenticate(user=self.student)
        gen_url = reverse('ai_instructor_generate')
        res = self.client.post(gen_url, {
            'skill_id': self.skill.id,
            'difficulty': 'Intermediate',
            'question_count': 2
        })
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
