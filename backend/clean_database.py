"""
SkillNova AI - Production Database Cleanup Script
Performs precise data cleanup without modifying database schema, models, or migrations.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from django.contrib.auth import get_user_model
from accounts.models import Skill, StudentProfile, InstructorProfile, StudentSkill
from assessments.models import Assessment, AssessmentQuestion, PersonalizedRoadmap
from ai.models import AIGeneratedQuestionBank, AIChatMessage, InterviewSession
from notifications.models import Notification
from resumes.models import ResumeAnalysis

User = get_user_model()

def clean_database():
    print("=" * 60)
    print("SKILLNOVA AI - PRE-DEPLOYMENT DATA CLEANUP")
    print("=" * 60)

    # 1. Verify backup exists
    backup_file = os.path.join(os.path.dirname(__file__), 'db_backup_pre_cleanup_20260927.sqlite3')
    if not os.path.exists(backup_file):
        raise RuntimeError(f"Backup file not found at {backup_file}! Aborting cleanup.")
    print(f"Verified database backup exists at: {backup_file}")

    with transaction.atomic():
        # 2. Delete test/demo assessment attempts and questions
        deleted_aq, _ = AssessmentQuestion.objects.all().delete()
        deleted_a, _ = Assessment.objects.all().delete()
        deleted_ss, _ = StudentSkill.objects.all().delete()
        print(f"Deleted {deleted_a} test assessment attempts, {deleted_aq} session questions, and {deleted_ss} test skill records.")

        # 3. Delete obsolete course/roadmap data
        deleted_rm, _ = PersonalizedRoadmap.objects.all().delete()
        print(f"Deleted {deleted_rm} obsolete personalized roadmap records.")

        # Clean temporary verification users
        deleted_v, _ = User.objects.filter(email__startswith='verify_').delete()
        if deleted_v:
            print(f"Deleted {deleted_v} temporary verification accounts.")

        # 4. Delete test notifications
        deleted_n, _ = Notification.objects.all().delete()
        print(f"Deleted {deleted_n} test notifications.")

        # 5. Delete test mock interviews and resume analyses
        deleted_iv, _ = InterviewSession.objects.all().delete()
        deleted_ra, _ = ResumeAnalysis.objects.all().delete()
        print(f"Deleted {deleted_iv} test interview sessions and {deleted_ra} test resume analyses.")

        # 6. Delete test AI chat messages
        deleted_cm, _ = AIChatMessage.objects.all().delete()
        print(f"Deleted {deleted_cm} test AI assistant chat messages.")

        # 7. Clean question bank: remove dummy test draft questions (CSS duplicates Q7-16)
        dummy_css_qs = AIGeneratedQuestionBank.objects.filter(
            skill__name='CSS',
            question_text__icontains='architectural principle'
        ) | AIGeneratedQuestionBank.objects.filter(
            skill__name='CSS',
            question_text__icontains='dependency isolation'
        ) | AIGeneratedQuestionBank.objects.filter(
            skill__name='CSS',
            question_text__icontains='error propagation'
        ) | AIGeneratedQuestionBank.objects.filter(
            skill__name='CSS',
            question_text__icontains='diagnosing performance'
        ) | AIGeneratedQuestionBank.objects.filter(
            skill__name='CSS',
            question_text__icontains='standard engineering practice'
        )
        deleted_dq, _ = dummy_css_qs.delete()
        print(f"Deleted {deleted_dq} dummy/duplicate test draft questions from question bank.")

        # 8. Ensure instructor account exists for question bank authorship
        instructor = User.objects.filter(role='INSTRUCTOR').first()
        if not instructor:
            raise RuntimeError("No instructor account found in database!")
        print(f"Verified Instructor account: {instructor.email} ({instructor.role})")

        # 9. Seed high-quality verified questions for skills that lack published bank questions
        seed_questions = [
            # JavaScript
            {
                'skill_name': 'JavaScript',
                'topic': 'Language Fundamentals',
                'difficulty': 'Intermediate',
                'question_text': "How does the JavaScript event loop handle the execution of microtasks (e.g., Promise callbacks) relative to macrotasks (e.g., setTimeout)?",
                'option_a': "Microtasks are always executed after all macrotasks in the event queue have completed.",
                'option_b': "All queued microtasks are executed immediately after the current task finishes and before the next macrotask is processed.",
                'option_c': "Microtasks and macrotasks run in parallel across separate OS threads.",
                'option_d': "Microtasks are only executed when the browser tab is idle or hidden.",
                'correct_option': 'B',
                'explanation': "The JavaScript event loop drains the entire microtask queue right after the current execution context completes and before processing the next macrotask from the task queue.",
            },
            {
                'skill_name': 'JavaScript',
                'topic': 'Types & Coercion',
                'difficulty': 'Beginner',
                'question_text': "What is the return value of evaluating 'typeof NaN' in JavaScript?",
                'option_a': "'nan'",
                'option_b': "'undefined'",
                'option_c': "'number'",
                'option_d': "'object'",
                'correct_option': 'C',
                'explanation': "In JavaScript, NaN represents 'Not-a-Number', but its data type is officially numeric according to IEEE 754, so typeof NaN evaluates to 'number'.",
            },
            # HTML
            {
                'skill_name': 'HTML',
                'topic': 'Semantic Structure',
                'difficulty': 'Beginner',
                'question_text': "What is the primary benefit of using semantic HTML elements such as <header>, <nav>, <main>, and <article> instead of generic <div> tags?",
                'option_a': "Semantic elements automatically render interactive UI animations without CSS.",
                'option_b': "They improve document accessibility for screen readers and enable search engine bots to accurately understand page hierarchy.",
                'option_c': "Semantic elements encrypt HTML source code transmitted over HTTP connections.",
                'option_d': "They eliminate the need for JavaScript event listeners.",
                'correct_option': 'B',
                'explanation': "Semantic HTML provides contextual meaning to user agents, assistive technologies (screen readers), and search crawler algorithms, enhancing accessibility and SEO.",
            },
            # CSS
            {
                'skill_name': 'CSS',
                'topic': 'Layout Models',
                'difficulty': 'Intermediate',
                'question_text': "What is the fundamental architectural difference between CSS Flexbox and CSS Grid layout systems?",
                'option_a': "Flexbox is designed for 1-dimensional layouts (rows or columns), while CSS Grid is designed for 2-dimensional layouts (simultaneous rows and columns).",
                'option_b': "Flexbox only works with text content, whereas CSS Grid only supports images and video elements.",
                'option_c': "CSS Grid requires a separate JavaScript polyfill in all modern web browsers.",
                'option_d': "Flexbox cannot align child elements along a cross-axis.",
                'correct_option': 'A',
                'explanation': "CSS Flexbox operates along a single dimension at a time (main-axis row or column), while CSS Grid handles complex two-dimensional spatial layouts simultaneously.",
            },
            {
                'skill_name': 'CSS',
                'topic': 'Box Model',
                'difficulty': 'Beginner',
                'question_text': "When the CSS rule 'box-sizing: border-box;' is applied to an element, how are its specified 'width' and 'height' calculated?",
                'option_a': "Width includes content only; padding and border are added outside the width.",
                'option_b': "Width includes content, padding, and border, keeping the total rendered footprint strictly equal to the specified dimensions.",
                'option_c': "Width includes margin and outline, but excludes padding and border.",
                'option_d': "Width is dynamically scaled to 100% of the parent container automatically.",
                'correct_option': 'B',
                'explanation': "With box-sizing: border-box, the specified width and height encompass content, padding, and borders, preventing elements from expanding beyond their defined bounds.",
            },
            # REST APIs
            {
                'skill_name': 'REST APIs',
                'topic': 'HTTP Semantics',
                'difficulty': 'Intermediate',
                'question_text': "According to REST and HTTP/1.1 specifications, which of the following HTTP methods is defined as idempotent and intended for complete resource replacement?",
                'option_a': "POST",
                'option_b': "PATCH",
                'option_c': "PUT",
                'option_d': "CONNECT",
                'correct_option': 'C',
                'explanation': "PUT is defined as idempotent (multiple identical requests have the exact same side-effects as a single request) and is used to create or overwrite a complete resource representation.",
            },
            # Git
            {
                'skill_name': 'Git',
                'topic': 'Version Control Workflows',
                'difficulty': 'Intermediate',
                'question_text': "What is the primary difference between running 'git merge feature-branch' and 'git rebase main' on a feature branch?",
                'option_a': "Merge preserves chronological history by creating a two-parent merge commit; rebase rewrites history by reapplying commits onto the tip of the target branch.",
                'option_b': "Rebase creates a merge commit, while merge always deletes the branch history.",
                'option_c': "Git rebase automatically pushes all local changes to the remote repository without confirmation.",
                'option_d': "Git merge cannot resolve conflicting file edits.",
                'correct_option': 'A',
                'explanation': "git merge combines branches with a dedicated merge commit preserving exact commit history; git rebase moves the feature branch base to the tip of main for a linear commit history.",
            },
            # Data Structures
            {
                'skill_name': 'Data Structures',
                'topic': 'Binary Trees',
                'difficulty': 'Intermediate',
                'question_text': "What is the average time complexity for search, insertion, and deletion operations in a self-balancing binary search tree (such as an AVL or Red-Black Tree)?",
                'option_a': "O(1)",
                'option_b': "O(n)",
                'option_c': "O(log n)",
                'option_d': "O(n log n)",
                'correct_option': 'C',
                'explanation': "Because self-balancing binary search trees maintain an approximately balanced tree height of O(log n), search, insert, and delete operations execute in O(log n) time.",
            },
            # Machine Learning
            {
                'skill_name': 'Machine Learning',
                'topic': 'Model Evaluation',
                'difficulty': 'Intermediate',
                'question_text': "In supervised machine learning, what does the term 'overfitting' describe?",
                'option_a': "The model performs exceptionally well on unseen test data but poorly on the training dataset.",
                'option_b': "The model learns training data noise and idiosyncratic patterns so closely that it fails to generalize accurately to new, unseen data.",
                'option_c': "The model has too few parameters to capture the underlying data patterns.",
                'option_d': "The model's training loss never decreases below 50%.",
                'correct_option': 'B',
                'explanation': "Overfitting occurs when high-variance models memorize the training set (including noise), resulting in low training error but poor generalization error on unseen validation/test data.",
            },
        ]

        added_qs = 0
        for sq in seed_questions:
            try:
                skill_obj = Skill.objects.get(name=sq['skill_name'])
                exists = AIGeneratedQuestionBank.objects.filter(
                    skill=skill_obj,
                    question_text=sq['question_text']
                ).exists()
                if not exists:
                    AIGeneratedQuestionBank.objects.create(
                        instructor=instructor,
                        skill=skill_obj,
                        topic=sq['topic'],
                        difficulty=sq['difficulty'],
                        question_text=sq['question_text'],
                        option_a=sq['option_a'],
                        option_b=sq['option_b'],
                        option_c=sq['option_c'],
                        option_d=sq['option_d'],
                        correct_option=sq['correct_option'],
                        explanation=sq['explanation'],
                        is_reviewed=True,
                        is_published=True
                    )
                    added_qs += 1
            except Skill.DoesNotExist:
                print(f"Warning: Skill '{sq['skill_name']}' not found in database.")

        print(f"Seeded {added_qs} verified production assessment questions into question bank.")
        total_bank_qs = AIGeneratedQuestionBank.objects.count()
        print(f"Total verified questions in question bank now: {total_bank_qs}")

        # 10. Delete demo student account
        demo_student = User.objects.filter(email='student@skillnova.ai').first()
        if demo_student:
            StudentSkill.objects.filter(student=demo_student).delete()
            StudentProfile.objects.filter(user=demo_student).delete()
            demo_student.delete()
            print("Deleted demo student account: student@skillnova.ai")
        else:
            print("No demo student account 'student@skillnova.ai' found.")

        # 11. Verify Admin account
        admin_user = User.objects.filter(role='ADMIN').first()
        if not admin_user:
            raise RuntimeError("No Admin account found in database!")
        print(f"Verified Admin account: {admin_user.email} (is_superuser={admin_user.is_superuser})")

    print("=" * 60)
    print("PRE-DEPLOYMENT DATABASE CLEANUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    clean_database()
