import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User, StudentProfile, InstructorProfile, Skill, StudentSkill
from assessments.models import Assessment, AssessmentQuestion, PersonalizedRoadmap
from notifications.models import Notification
from ai.models import AIChatMessage, InterviewSession, AIGeneratedQuestionBank


class Command(BaseCommand):
    help = "Seed SkillNova AI with demo users, 11 skills, question bank, assessments, and notifications."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding SkillNova AI database..."))

        # 1. Admin User
        admin_user, _ = User.objects.get_or_create(
            email='admin@skillnova.ai',
            defaults={
                'username': 'admin',
                'first_name': 'Sarah',
                'last_name': 'Connor',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
                'avatar': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300&auto=format&fit=crop&q=80'
            }
        )
        admin_user.set_password('Admin@123')
        admin_user.save()

        # 2. Instructor User
        instructor_user, _ = User.objects.get_or_create(
            email='instructor@skillnova.ai',
            defaults={
                'username': 'instructor',
                'first_name': 'Dr. Marcus',
                'last_name': 'Vance',
                'role': 'INSTRUCTOR',
                'avatar': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&auto=format&fit=crop&q=80'
            }
        )
        instructor_user.set_password('Instructor@123')
        instructor_user.save()
        InstructorProfile.objects.get_or_create(
            user=instructor_user,
            defaults={
                'title': 'Senior Assessment Architect & Technical Evaluator',
                'organization': 'SkillNova AI Evaluation Board',
                'expertise': 'Python, Distributed Systems, Django, React, AI Applications',
                'verified': True
            }
        )

        # 3. Student User
        student_user, _ = User.objects.get_or_create(
            email='student@skillnova.ai',
            defaults={
                'username': 'student',
                'first_name': 'Alex',
                'last_name': 'Morgan',
                'role': 'STUDENT',
                'avatar': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&auto=format&fit=crop&q=80'
            }
        )
        student_user.set_password('Student@123')
        student_user.save()
        StudentProfile.objects.get_or_create(
            user=student_user,
            defaults={
                'current_education': 'B.Tech in Computer Science & Engineering',
                'target_role': 'Python Full Stack Developer',
                'experience_level': 'Fresher',
                'github_url': 'https://github.com/alexmorgan-dev',
                'linkedin_url': 'https://linkedin.com/in/alexmorgan',
                'streak_days': 7,
                'points': 420
            }
        )

        # 4. Initial 11 Skills
        skills_data = [
            {
                "name": "Python",
                "slug": "python",
                "category": "Programming",
                "difficulty": "Beginner",
                "description": "High-level, interpreted programming language renowned for clean syntax, versatile libraries, and AI prominence.",
                "topics": ["Variables & Data Types", "Functions & Scopes", "OOP & Classes", "Decorators & Generators", "Exception Handling", "File I/O"],
                "icon": "FaPython"
            },
            {
                "name": "Django",
                "slug": "django",
                "category": "Framework",
                "difficulty": "Intermediate",
                "description": "High-level Python web framework with built-in ORM, authentication, admin panel, and REST framework integration.",
                "topics": ["MVT Architecture", "Django ORM & QuerySets", "Migrations", "DRF Serializers", "JWT Authentication", "Middleware & Signals"],
                "icon": "SiDjango"
            },
            {
                "name": "JavaScript",
                "slug": "javascript",
                "category": "Programming",
                "difficulty": "Beginner",
                "description": "The foundational language of the modern web, powering interactive browser experiences and Node.js servers.",
                "topics": ["ES6+ Syntax", "Event Loop & Async/Await", "Closures & Prototypes", "DOM Manipulation", "Promises", "Fetch API"],
                "icon": "FaJs"
            },
            {
                "name": "React",
                "slug": "react",
                "category": "Framework",
                "difficulty": "Intermediate",
                "description": "Declarative, component-based frontend library for building reactive single-page client applications.",
                "topics": ["JSX & Virtual DOM", "Hooks (useState, useEffect)", "Context API", "Component Lifecycle", "Performance Memoization", "Routing"],
                "icon": "FaReact"
            },
            {
                "name": "SQL",
                "slug": "sql",
                "category": "Database",
                "difficulty": "Beginner",
                "description": "Standard declarative query language for relational database management systems and query performance optimization.",
                "topics": ["SELECT & Filtering", "Joins (INNER, LEFT, RIGHT)", "Aggregations & GROUP BY", "Subqueries", "Indexing & Explain", "Transactions & ACID"],
                "icon": "FaDatabase"
            },
            {
                "name": "HTML",
                "slug": "html",
                "category": "Core CS",
                "difficulty": "Beginner",
                "description": "Hypertext Markup Language structuring web documents, accessibility trees, and semantic content.",
                "topics": ["Semantic Tags", "Forms & Validation", "Accessibility (a11y)", "SEO Meta Tags", "Canvas & Audio/Video", "Responsive Meta"],
                "icon": "FaHtml5"
            },
            {
                "name": "CSS",
                "slug": "css",
                "category": "Core CS",
                "difficulty": "Beginner",
                "description": "Cascading Style Sheets powering layout models, visual aesthetics, responsive design, and CSS animations.",
                "topics": ["Flexbox Layout", "CSS Grid", "Box Model & Stacking", "Responsive Media Queries", "Transitions & Keyframes", "CSS Variables"],
                "icon": "FaCss3"
            },
            {
                "name": "REST APIs",
                "slug": "rest-apis",
                "category": "Framework",
                "difficulty": "Intermediate",
                "description": "Architectural principles for designing scalable, stateless, standard HTTP client-server communication interfaces.",
                "topics": ["HTTP Methods & Status Codes", "Stateless Design", "Authentication & Tokens", "Pagination & Filtering", "Versioning", "CORS & Headers"],
                "icon": "FaNetworkWired"
            },
            {
                "name": "Git",
                "slug": "git",
                "category": "DevOps",
                "difficulty": "Beginner",
                "description": "Distributed version control system for tracking changes, branching strategies, and collaborative codebases.",
                "topics": ["Branching & Merging", "Rebasing vs Merging", "Git Stash & Cherry-Pick", "Conflict Resolution", "Remotes & Pull Requests", "Commit Conventions"],
                "icon": "FaGitAlt"
            },
            {
                "name": "Data Structures",
                "slug": "data-structures",
                "category": "Core CS",
                "difficulty": "Intermediate",
                "description": "Fundamental organization and algorithmic mechanisms for storing and retrieving computational data efficiently.",
                "topics": ["Arrays & Linked Lists", "Stacks & Queues", "Hash Tables", "Trees & BSTs", "Graphs & Traversal", "Big O Complexity Analysis"],
                "icon": "FaCodeBranch"
            },
            {
                "name": "Machine Learning",
                "slug": "machine-learning",
                "category": "AI/ML",
                "difficulty": "Advanced",
                "description": "Algorithmic paradigms empowering systems to discover patterns, make predictions, and generate intelligent decisions.",
                "topics": ["Supervised vs Unsupervised", "Regression & Classification", "Feature Engineering", "Neural Networks", "Model Evaluation Metrics", "LLMs & Prompt Engineering"],
                "icon": "FaBrain"
            }
        ]

        skill_objs = {}
        for s in skills_data:
            obj, _ = Skill.objects.update_or_create(
                slug=s["slug"],
                defaults={
                    "name": s["name"],
                    "category": s["category"],
                    "difficulty": s["difficulty"],
                    "description": s["description"],
                    "topics": s["topics"],
                    "icon": s["icon"]
                }
            )
            skill_objs[s["name"]] = obj

        # 5. Student Tracked Skills
        student_skills_data = [
            ("Python", "Intermediate", 78, 78.0),
            ("SQL", "Beginner", 86, 86.0),
            ("React", "Intermediate", 64, 64.0),
            ("Django", "Intermediate", 71, 71.0),
        ]
        for name, prof, prog, score in student_skills_data:
            if name in skill_objs:
                StudentSkill.objects.update_or_create(
                    student=student_user,
                    skill=skill_objs[name],
                    defaults={
                        "proficiency_level": prof,
                        "progress_percentage": prog,
                        "assessment_score": score,
                        "last_assessed": timezone.now()
                    }
                )

        # 6. Seed Question Bank in AIGeneratedQuestionBank (Instructor Approved)
        questions_pool = [
            {
                "skill": "Python",
                "topic": "Functions & Scopes",
                "difficulty": "Intermediate",
                "question": "What is the difference between a list and a tuple in Python?",
                "option_a": "Lists are immutable; tuples are mutable.",
                "option_b": "Lists are mutable and use square brackets; tuples are immutable and use parentheses.",
                "option_c": "Tuples cannot hold heterogeneous data types; lists can.",
                "option_d": "Tuples consume more memory than lists for the same elements.",
                "correct_option": 1,
                "explanation": "In Python, lists are mutable (can be altered in place) and denoted by [], whereas tuples are immutable (read-only fixed sequences) denoted by ()."
            },
            {
                "skill": "Python",
                "topic": "OOP & Classes",
                "difficulty": "Intermediate",
                "question": "In Python, what is the role of the '__init__' method in a class definition?",
                "option_a": "To allocate raw operating system memory for the class.",
                "option_b": "To initialize the instance attributes upon object creation.",
                "option_c": "To destroy unreferenced class objects automatically.",
                "option_d": "To make class methods accessible globally without instantiation.",
                "correct_option": 1,
                "explanation": "__init__ serves as the instance initializer in Python, executing immediately after __new__ constructs the object."
            },
            {
                "skill": "Python",
                "topic": "Decorators & Generators",
                "difficulty": "Advanced",
                "question": "What keyword is used to turn a regular Python function into a generator that produces values lazily?",
                "option_a": "produce",
                "option_b": "yield",
                "option_c": "emit",
                "option_d": "defer",
                "correct_option": 1,
                "explanation": "The 'yield' statement suspends execution, returning the current value while preserving local execution state for subsequent iterations."
            },
            {
                "skill": "Django",
                "topic": "Django ORM & QuerySets",
                "difficulty": "Intermediate",
                "question": "How does 'select_related' differ from 'prefetch_related' in the Django ORM?",
                "option_a": "select_related does SQL JOINs for foreign keys; prefetch_related executes separate queries for many-to-many relationships in Python.",
                "option_b": "prefetch_related performs an inner join, while select_related uses a cross join.",
                "option_c": "select_related only functions with PostgreSQL databases.",
                "option_d": "They are identical aliases for database joins.",
                "correct_option": 0,
                "explanation": "select_related follows single-valued foreign keys using SQL JOIN. prefetch_related retrieves multi-valued relations (many-to-many, reverse FK) in separate queries and joins them in Python memory."
            },
            {
                "skill": "SQL",
                "topic": "SELECT & Filtering",
                "difficulty": "Beginner",
                "question": "What is the key difference between the WHERE and HAVING clauses in SQL?",
                "option_a": "WHERE filters grouped aggregates; HAVING filters individual rows before grouping.",
                "option_b": "WHERE filters rows before aggregation; HAVING filters aggregated groups after GROUP BY.",
                "option_c": "HAVING can only be applied to string columns.",
                "option_d": "WHERE is only supported in MySQL; HAVING is used in Oracle.",
                "correct_option": 1,
                "explanation": "WHERE filters row records before any aggregation is calculated; HAVING filters aggregate outcomes computed by GROUP BY."
            },
            {
                "skill": "React",
                "topic": "Hooks (useState, useEffect)",
                "difficulty": "Intermediate",
                "question": "When does the cleanup function returned from a React 'useEffect' hook execute?",
                "option_a": "Only when the entire browser window is refreshed.",
                "option_b": "Before the component re-runs the effect on subsequent renders and when the component unmounts.",
                "option_c": "Synchronously before the initial HTML paint on the screen.",
                "option_d": "Never unless an unhandled error is thrown in the render cycle.",
                "correct_option": 1,
                "explanation": "React runs effect cleanups prior to re-applying the effect on changes to dependencies, as well as on component unmounting."
            }
        ]

        for q in questions_pool:
            skill_inst = skill_objs.get(q["skill"])
            if skill_inst:
                AIGeneratedQuestionBank.objects.update_or_create(
                    skill=skill_inst,
                    question_text=q["question"],
                    defaults={
                        "instructor": instructor_user,
                        "topic": q["topic"],
                        "difficulty": q["difficulty"],
                        "option_a": q["option_a"],
                        "option_b": q["option_b"],
                        "option_c": q["option_c"],
                        "option_d": q["option_d"],
                        "correct_option": ["A", "B", "C", "D"][q["correct_option"]],
                        "explanation": q["explanation"],
                        "is_reviewed": True,
                        "is_published": True,
                    }
                )

        # 7. Seed Past Assessments for Student (Matching Dashboard & History specs)
        # Assessment 1: Python - 78% (Intermediate) (23/30)
        a1, _ = Assessment.objects.update_or_create(
            student=student_user,
            skill=skill_objs["Python"],
            defaults={
                "difficulty": "Intermediate",
                "question_count": 30,
                "score": 23,
                "percentage": 78.0,
                "skill_level": "Intermediate",
                "strong_areas": ["Functions & Scopes", "Lists & Tuples", "Dictionaries"],
                "weak_areas": ["Object-Oriented Programming", "Exception Handling", "Decorators"],
                "recommendations": [
                    "Revise Python OOP (Encapsulation, Class Inheritance, and Polymorphism)",
                    "Practice robust exception handling with custom error types",
                    "Take another intermediate assessment to verify mastery"
                ],
                "is_completed": True,
                "completed_at": timezone.now() - timezone.timedelta(days=1)
            }
        )

        # Create questions for a1
        AssessmentQuestion.objects.update_or_create(
            assessment=a1,
            question_text="What is the difference between a list and a tuple in Python?",
            defaults={
                "topic": "Data Types",
                "difficulty": "Intermediate",
                "option_a": "Lists are immutable; tuples are mutable.",
                "option_b": "Lists are mutable and use []; tuples are immutable and use ().",
                "option_c": "Tuples cannot store strings.",
                "option_d": "Lists cannot be nested.",
                "correct_option": "B",
                "user_answer": "B",
                "is_correct": True,
                "explanation": "Lists are mutable while tuples cannot be altered after instantiation."
            }
        )
        AssessmentQuestion.objects.update_or_create(
            assessment=a1,
            question_text="What method initializes instance attributes in Python classes?",
            defaults={
                "topic": "OOP",
                "difficulty": "Intermediate",
                "option_a": "__init__",
                "option_b": "__new__",
                "option_c": "__str__",
                "option_d": "__main__",
                "correct_option": "A",
                "user_answer": "A",
                "is_correct": True,
                "explanation": "__init__ initializes attributes on new instances."
            }
        )

        # Assessment 2: SQL - 86% (Beginner) (26/30)
        a2, _ = Assessment.objects.update_or_create(
            student=student_user,
            skill=skill_objs["SQL"],
            defaults={
                "difficulty": "Beginner",
                "question_count": 30,
                "score": 26,
                "percentage": 86.0,
                "skill_level": "Strong",
                "strong_areas": ["SELECT & Filtering", "Basic Joins", "Aggregations"],
                "weak_areas": ["Subqueries", "Indexing"],
                "recommendations": [
                    "Explore correlated subqueries and CTEs (Common Table Expressions)",
                    "Study B-Tree index structures and query optimization plans"
                ],
                "is_completed": True,
                "completed_at": timezone.now() - timezone.timedelta(days=2)
            }
        )

        # Assessment 3: React - 64% (Intermediate) (19/30)
        a3, _ = Assessment.objects.update_or_create(
            student=student_user,
            skill=skill_objs["React"],
            defaults={
                "difficulty": "Intermediate",
                "question_count": 30,
                "score": 19,
                "percentage": 64.0,
                "skill_level": "Needs Practice",
                "strong_areas": ["JSX", "useState", "Props"],
                "weak_areas": ["useEffect Cleanup", "Context API", "useCallback"],
                "recommendations": [
                    "Review useEffect dependencies and cleanup subscriptions",
                    "Practice state lifting and React Context state propagation",
                    "Take a focused React Hooks diagnostic test"
                ],
                "is_completed": True,
                "completed_at": timezone.now() - timezone.timedelta(days=3)
            }
        )

        # 8. Seed Personalized Roadmap
        PersonalizedRoadmap.objects.update_or_create(
            student=student_user,
            skill=skill_objs["Python"],
            defaults={
                "title": "Python Career Readiness Progression",
                "stages": [
                    {"id": 1, "title": "Python Core & Syntax", "status": "completed", "topics": ["Variables", "Control Flow", "Functions"]},
                    {"id": 2, "title": "Data Structures & Collections", "status": "completed", "topics": ["Lists", "Tuples", "Dicts", "Sets"]},
                    {"id": 3, "title": "OOP & Class Architecture", "status": "recommended", "topics": ["Inheritance", "Polymorphism", "Dunder Methods"]},
                    {"id": 4, "title": "Exception Handling & I/O", "status": "recommended", "topics": ["Try/Except", "Custom Errors", "Context Managers"]},
                    {"id": 5, "title": "Advanced Decorators & Generators", "status": "current", "topics": ["Yield", "Closures", "Decorators"]},
                    {"id": 6, "title": "Web Frameworks & APIs", "status": "locked", "topics": ["Django", "DRF Serializers", "JWT"]}
                ]
            }
        )

        # 9. Seed Notifications
        notifications_data = [
            ("Python Assessment Completed", "You achieved 78% (Intermediate Level). Review your strong and weak topics now!", "assessment", f"/assessments/{a1.id}"),
            ("SQL Assessment Result", "You scored 86% in SQL Beginner Assessment! Rated: Strong.", "assessment", f"/assessments/{a2.id}"),
            ("Interview Practice Ready", "New mock interview sets for Python Developer are available in Interview Prep.", "interview", "/interview-prep"),
            ("Resume Analyzer", "Upload your updated resume to audit skill gaps against Python Developer positions.", "resume", "/resume-analyzer")
        ]

        for title, msg, n_type, link in notifications_data:
            Notification.objects.get_or_create(
                user=student_user,
                title=title,
                defaults={
                    "message": msg,
                    "notification_type": n_type,
                    "link": link,
                    "is_read": False
                }
            )

        self.stdout.write(self.style.SUCCESS("SkillNova AI database successfully seeded with demo assessment & readiness data!"))
