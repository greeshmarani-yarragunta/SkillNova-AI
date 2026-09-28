from django.core.management.base import BaseCommand
from accounts.models import Skill


class Command(BaseCommand):
    help = "Seed SkillNova AI production technical skills."

    def handle(self, *args, **options):
        skills_data = [
            {
                "name": "Python",
                "slug": "python",
                "category": "Programming",
                "difficulty": "Beginner",
                "description": "High-level, interpreted programming language renowned for clean syntax, versatile libraries, and AI prominence.",
                "topics": [
                    "Variables & Data Types",
                    "Functions & Scopes",
                    "OOP & Classes",
                    "Decorators & Generators",
                    "Exception Handling",
                    "File I/O",
                ],
                "icon": "FaPython",
            },
            {
                "name": "Django",
                "slug": "django",
                "category": "Framework",
                "difficulty": "Intermediate",
                "description": "High-level Python web framework with built-in ORM, authentication, admin panel, and REST framework integration.",
                "topics": [
                    "MVT Architecture",
                    "Django ORM & QuerySets",
                    "Migrations",
                    "DRF Serializers",
                    "JWT Authentication",
                    "Middleware & Signals",
                ],
                "icon": "SiDjango",
            },
            {
                "name": "JavaScript",
                "slug": "javascript",
                "category": "Programming",
                "difficulty": "Beginner",
                "description": "The foundational language of the modern web, powering interactive browser experiences and Node.js servers.",
                "topics": [
                    "ES6+ Syntax",
                    "Event Loop & Async/Await",
                    "Closures & Prototypes",
                    "DOM Manipulation",
                    "Promises",
                    "Fetch API",
                ],
                "icon": "FaJs",
            },
            {
                "name": "React",
                "slug": "react",
                "category": "Framework",
                "difficulty": "Intermediate",
                "description": "Declarative, component-based frontend library for building reactive single-page client applications.",
                "topics": [
                    "JSX & Virtual DOM",
                    "Hooks (useState, useEffect)",
                    "Context API",
                    "Component Lifecycle",
                    "Performance Memoization",
                    "Routing",
                ],
                "icon": "FaReact",
            },
            {
                "name": "SQL",
                "slug": "sql",
                "category": "Database",
                "difficulty": "Beginner",
                "description": "Standard declarative query language for relational database management systems and query performance optimization.",
                "topics": [
                    "SELECT & Filtering",
                    "Joins (INNER, LEFT, RIGHT)",
                    "Aggregations & GROUP BY",
                    "Subqueries",
                    "Indexing & Explain",
                    "Transactions & ACID",
                ],
                "icon": "FaDatabase",
            },
            {
                "name": "HTML",
                "slug": "html",
                "category": "Core CS",
                "difficulty": "Beginner",
                "description": "Hypertext Markup Language structuring web documents, accessibility trees, and semantic content.",
                "topics": [
                    "Semantic Tags",
                    "Forms & Validation",
                    "Accessibility (a11y)",
                    "SEO Meta Tags",
                    "Canvas & Audio/Video",
                    "Responsive Meta",
                ],
                "icon": "FaHtml5",
            },
            {
                "name": "CSS",
                "slug": "css",
                "category": "Core CS",
                "difficulty": "Beginner",
                "description": "Cascading Style Sheets powering layout models, visual aesthetics, responsive design, and CSS animations.",
                "topics": [
                    "Flexbox Layout",
                    "CSS Grid",
                    "Box Model & Stacking",
                    "Responsive Media Queries",
                    "Transitions & Keyframes",
                    "CSS Variables",
                ],
                "icon": "FaCss3",
            },
            {
                "name": "REST APIs",
                "slug": "rest-apis",
                "category": "Framework",
                "difficulty": "Intermediate",
                "description": "Architectural principles for designing scalable, stateless, standard HTTP client-server communication interfaces.",
                "topics": [
                    "HTTP Methods & Status Codes",
                    "Stateless Design",
                    "Authentication & Tokens",
                    "Pagination & Filtering",
                    "Versioning",
                    "CORS & Headers",
                ],
                "icon": "FaNetworkWired",
            },
            {
                "name": "Git",
                "slug": "git",
                "category": "DevOps",
                "difficulty": "Beginner",
                "description": "Distributed version control system for tracking changes, branching strategies, and collaborative codebases.",
                "topics": [
                    "Branching & Merging",
                    "Rebasing vs Merging",
                    "Git Stash & Cherry-Pick",
                    "Conflict Resolution",
                    "Remotes & Pull Requests",
                    "Commit Conventions",
                ],
                "icon": "FaGitAlt",
            },
            {
                "name": "Data Structures",
                "slug": "data-structures",
                "category": "Core CS",
                "difficulty": "Intermediate",
                "description": "Fundamental organization and algorithmic mechanisms for storing and retrieving computational data efficiently.",
                "topics": [
                    "Arrays & Linked Lists",
                    "Stacks & Queues",
                    "Hash Tables",
                    "Trees & BSTs",
                    "Graphs & Traversal",
                    "Big O Complexity Analysis",
                ],
                "icon": "FaCodeBranch",
            },
            {
                "name": "Machine Learning",
                "slug": "machine-learning",
                "category": "AI/ML",
                "difficulty": "Advanced",
                "description": "Algorithmic paradigms empowering systems to discover patterns, make predictions, and generate intelligent decisions.",
                "topics": [
                    "Supervised vs Unsupervised",
                    "Regression & Classification",
                    "Feature Engineering",
                    "Neural Networks",
                    "Model Evaluation Metrics",
                    "LLMs & Prompt Engineering",
                ],
                "icon": "FaBrain",
            },
        ]

        created_count = 0
        updated_count = 0

        for skill_data in skills_data:
            _, created = Skill.objects.update_or_create(
                slug=skill_data["slug"],
                defaults={
                    "name": skill_data["name"],
                    "category": skill_data["category"],
                    "difficulty": skill_data["difficulty"],
                    "description": skill_data["description"],
                    "topics": skill_data["topics"],
                    "icon": skill_data["icon"],
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Production skills seeded successfully. "
                f"Created: {created_count}, Updated: {updated_count}"
            )
        )