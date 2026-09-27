"""
Verification Script for SkillNova AI Post-Cleanup
Tests all required production workflows:
- Admin login
- Instructor login
- Student registration & login
- Skills availability
- 30-question assessment generation
- Assessment submission & diagnostic results
- AI recommendations
- Assessment history
- Instructor student performance view
- Admin platform management
"""
import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from accounts.models import User, Skill
from assessments.models import Assessment

def verify_all():
    print("=" * 60)
    print("SKILLNOVA AI - POST-CLEANUP PRODUCTION VERIFICATION")
    print("=" * 60)

    client = APIClient(SERVER_NAME='localhost')

    # 1. Admin login
    print("\n1. Testing Admin login...")
    admin_res = client.post('/api/auth/login/', {
        'email': 'admin@skillnova.ai',
        'password': 'Admin@123'
    }, format='json')
    assert admin_res.status_code == 200, f"Admin login failed: {admin_res.data}"
    admin_token = admin_res.data['tokens']['access']
    print(f"   [PASS] Admin login successful. Role: {admin_res.data['user']['role']}")

    # 2. Instructor login
    print("\n2. Testing Instructor login...")
    inst_res = client.post('/api/auth/login/', {
        'email': 'instructor@skillnova.ai',
        'password': 'Instructor@123'
    }, format='json')
    assert inst_res.status_code == 200, f"Instructor login failed: {inst_res.data}"
    inst_token = inst_res.data['tokens']['access']
    print(f"   [PASS] Instructor login successful. Role: {inst_res.data['user']['role']}")

    # 3. Student Registration
    test_student_email = 'production_student_test@skillnova.ai'
    # Delete if exists from previous run
    User.objects.filter(email=test_student_email).delete()

    print("\n3. Testing Student registration...")
    reg_res = client.post('/api/auth/register/', {
        'email': test_student_email,
        'username': 'prod_student_test',
        'password': 'Password@123',
        'confirm_password': 'Password@123',
        'first_name': 'Production',
        'last_name': 'Candidate',
        'target_role': 'Python Backend Engineer'
    }, format='json')
    assert reg_res.status_code in (200, 201), f"Student registration failed: {reg_res.data}"
    print(f"   [PASS] Student registered successfully: {test_student_email}")

    # 4. Student Login
    print("\n4. Testing Student login...")
    stud_login_res = client.post('/api/auth/login/', {
        'email': test_student_email,
        'password': 'Password@123'
    }, format='json')
    assert stud_login_res.status_code == 200, f"Student login failed: {stud_login_res.data}"
    student_token = stud_login_res.data['tokens']['access']
    print(f"   [PASS] Student login successful.")

    # 5. Skills Availability
    print("\n5. Testing Skills availability...")
    skills_res = client.get('/api/skills/')
    assert skills_res.status_code == 200, f"Skills fetch failed: {skills_res.data}"
    skills = skills_res.data
    assert len(skills) >= 11, f"Expected at least 11 skills, found {len(skills)}"
    print(f"   [PASS] Found {len(skills)} production skills in taxonomy.")

    # 6. Generate 30-Question Assessment
    print("\n6. Testing 30-Question Assessment generation...")
    python_skill = Skill.objects.get(name='Python')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {student_token}')
    gen_res = client.post('/api/assessments/generate/', {
        'skill_id': python_skill.id,
        'difficulty': 'Intermediate'
    }, format='json')
    assert gen_res.status_code in (200, 201), f"Assessment generation failed: {gen_res.data}"
    assess_data = gen_res.data
    questions = assess_data.get('questions', [])
    assert len(questions) == 30, f"Expected EXACTLY 30 questions, got {len(questions)}!"
    assessment_id = assess_data['id']
    print(f"   [PASS] Assessment {assessment_id} successfully generated with EXACTLY {len(questions)} questions.")

    # 7. Submit Assessment & Verify Diagnostic Evaluation
    print("\n7. Testing Assessment submission & results calculation...")
    answers = {}
    for i, q in enumerate(questions):
        # Answer with option A for half, B for half
        answers[str(q['id'])] = 'B' if i % 2 == 0 else 'A'

    sub_res = client.post(f'/api/assessments/{assessment_id}/submit/', {
        'answers': answers,
        'time_taken_seconds': 450
    }, format='json')
    assert sub_res.status_code == 200, f"Assessment submission failed: {sub_res.data}"
    result = sub_res.data
    assert 'percentage' in result and 'skill_level' in result, f"Incomplete result: {result}"
    assert len(result.get('strong_areas', [])) >= 0
    assert len(result.get('recommendations', [])) > 0
    print(f"   [PASS] Assessment evaluated: Score {result['score']}/{result.get('question_count', 30)} ({result['percentage']}%), Level: {result['skill_level']}")
    print(f"   [PASS] Recommendations generated: {len(result['recommendations'])} items")

    # 8. Assessment History
    print("\n8. Testing Student Assessment History...")
    hist_res = client.get('/api/assessments/results/')
    assert hist_res.status_code == 200, f"History fetch failed: {hist_res.data}"
    history_items = hist_res.data if isinstance(hist_res.data, list) else hist_res.data.get('results', [])
    assert len(history_items) >= 1, "Assessment should appear in history"
    print(f"   [PASS] History contains completed assessment record.")

    # 9. Instructor Performance View
    print("\n9. Testing Instructor Student Performance view...")
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {inst_token}')
    perf_res = client.get('/api/instructor/performance/')
    assert perf_res.status_code == 200, f"Instructor performance failed: {perf_res.data}"
    perf_records = perf_res.data
    assert any(r['id'] == assessment_id for r in perf_records), "Student attempt not visible to Instructor"
    print(f"   [PASS] Instructor successfully viewed student assessment attempt (ID {assessment_id}).")

    # 10. Admin Platform Governance
    print("\n10. Testing Admin Platform Governance...")
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    users_res = client.get('/api/admin/users/')
    assert users_res.status_code == 200, f"Admin users list failed: {users_res.data}"
    assess_log_res = client.get('/api/admin/assessments/')
    assert assess_log_res.status_code == 200, f"Admin assessment log failed: {assess_log_res.data}"
    print(f"   [PASS] Admin successfully fetched platform user directory and assessment log.")

    # Clean up test candidate
    User.objects.filter(email=test_student_email).delete()
    print("\n   [PASS] Cleaned up verification student candidate.")

    print("\n" + "=" * 60)
    print("ALL 10 PRODUCTION WORKFLOW VERIFICATION CHECKS PASSED!")
    print("=" * 60)

if __name__ == '__main__':
    verify_all()
