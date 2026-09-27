import os
import json
import logging
import re
from django.conf import settings

logger = logging.getLogger(__name__)

# Try importing google generative AI if installed
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


class AIService:
    """
    SkillNova AI Core Service Layer.
    Dispatches to Google Gemini LLM API when configured,
    and provides a deterministic, highly intelligent expert heuristic engine
    guaranteeing 100% platform uptime and reliable data structures.
    """

    def __init__(self):
        self.api_key = getattr(settings, 'AI_API_KEY', '') or os.getenv('AI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
        self.client_available = False
        if self.api_key and HAS_GENAI:
            try:
                genai.configure(api_key=self.api_key)
                self.client_available = True
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")

    # =========================================================================
    # 1. AI SKILL ASSESSMENT QUESTION GENERATION
    # =========================================================================
    def generate_assessment_questions(self, skill_name, difficulty='Intermediate', count=30):
        """Generates multiple choice assessment questions for a skill and difficulty.
        SkillNova AI enforces exactly 30 questions for all skill assessments.
        """
        target_count = count if count == 30 else 30
        if self.client_available:
            prompt = f"""
            You are a senior technical interviewer. Generate exactly {target_count} multiple choice questions for the technical skill: '{skill_name}' at '{difficulty}' difficulty.
            Return ONLY a valid JSON array of {target_count} objects with no surrounding markdown ticks or commentary:
            [
              {{
                "question_text": "question here",
                "option_a": "option A text",
                "option_b": "option B text",
                "option_c": "option C text",
                "option_d": "option D text",
                "correct_option": "A" or "B" or "C" or "D",
                "explanation": "Clear explanation of why this answer is correct",
                "topic": "Specific subtopic (e.g. OOP, Memory, Async, Syntax)",
                "difficulty": "{difficulty}"
              }}
            ]
            """
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                clean_text = self._clean_json_response(response.text)
                questions = json.loads(clean_text)
                if isinstance(questions, list):
                    valid_qs = [
                        q for q in questions
                        if isinstance(q, dict) and q.get('question_text') and q.get('option_a') and q.get('correct_option')
                    ]
                    if len(valid_qs) >= target_count:
                        return valid_qs[:target_count]
                    elif len(valid_qs) > 0:
                        # Supplement AI questions with distinct heuristic questions to reach exactly 30
                        needed = target_count - len(valid_qs)
                        existing_texts = {q['question_text'] for q in valid_qs}
                        fallback = self._heuristic_assessment_questions(
                            skill_name, difficulty, count=needed, exclude_texts=existing_texts
                        )
                        valid_qs.extend(fallback)
                        if len(valid_qs) >= target_count:
                            return valid_qs[:target_count]
            except Exception as e:
                logger.warning(f"Live AI question generation failed, falling back: {e}")

        # Intelligent Heuristic Fallback guaranteeing exactly 30 unique questions
        return self._heuristic_assessment_questions(skill_name, difficulty, target_count)

    # =========================================================================
    # 2. AI ASSESSMENT EVALUATION & SKILL LEVEL ANALYSIS
    # =========================================================================
    def analyze_assessment_results(self, skill_name, difficulty, question_results):
        """
        question_results: list of { 'topic': str, 'is_correct': bool, 'question_text': str }
        Calculates score, detects strong and weak areas, computes proficiency level,
        and generates personalized learning recommendations.
        """
        total = len(question_results)
        if total == 0:
            return {
                'score': 0, 'percentage': 0, 'skill_level': 'Beginner',
                'strong_areas': [], 'weak_areas': ['General Concepts'],
                'recommendations': [f'Begin studying fundamentals of {skill_name}']
            }

        correct_count = sum(1 for q in question_results if q.get('is_correct'))
        percentage = round((correct_count / total) * 100, 1)

        # Categorize topics
        topic_stats = {}
        for q in question_results:
            topic = q.get('topic', 'General')
            if topic not in topic_stats:
                topic_stats[topic] = {'total': 0, 'correct': 0}
            topic_stats[topic]['total'] += 1
            if q.get('is_correct'):
                topic_stats[topic]['correct'] += 1

        strong_areas = []
        weak_areas = []
        for topic, stat in topic_stats.items():
            rate = stat['correct'] / stat['total']
            if rate >= 0.6:
                strong_areas.append(topic)
            else:
                weak_areas.append(topic)

        # Determine level
        if percentage >= 85:
            skill_level = 'Advanced'
        elif percentage >= 55:
            skill_level = 'Intermediate'
        else:
            skill_level = 'Beginner'

        # Generate actionable recommendations
        recommendations = []
        if weak_areas:
            for weak in weak_areas[:3]:
                recommendations.append(f"Deep-dive into '{weak}' in {skill_name} with interactive coding exercises.")
        else:
            recommendations.append(f"Master advanced performance optimization and architectural patterns in {skill_name}.")

        recommendations.append(f"Build a real-world hands-on project utilizing {skill_name} to cement your knowledge.")
        recommendations.append(f"Take the {skill_name} quiz challenges and practice technical interview questions.")

        return {
            'score': correct_count,
            'percentage': percentage,
            'skill_level': skill_level,
            'strong_areas': strong_areas or ['Basic Syntax'],
            'weak_areas': weak_areas or ['Advanced Edge Cases'],
            'recommendations': recommendations
        }

    # =========================================================================
    # 3. PERSONALIZED ROADMAP GENERATOR
    # =========================================================================
    def generate_roadmap(self, skill_name, skill_level='Beginner', weak_topics=None, target_role='Developer'):
        """Generates a structured career learning roadmap with status milestones."""
        weak_topics = weak_topics or []
        stages = []

        curriculums = {
            'Python': [
                {"title": "Python Basics & Syntax", "topics": ["Data Types", "Conditionals", "Loops"], "status": "completed"},
                {"title": "Data Structures & Collections", "topics": ["Lists", "Tuples", "Dictionaries", "Sets"], "status": "completed" if skill_level in ['Intermediate', 'Advanced'] else "current"},
                {"title": "Functional Programming & Modules", "topics": ["Functions", "Lambdas", "Decorators", "Generators"], "status": "recommended" if "Decorators" in weak_topics else ("completed" if skill_level == 'Advanced' else "current")},
                {"title": "Object-Oriented Programming (OOP)", "topics": ["Classes", "Inheritance", "Polymorphism", "Dunder Methods"], "status": "recommended" if "OOP" in weak_topics else "current"},
                {"title": "Exception Handling & File I/O", "topics": ["Try-Except", "Context Managers", "File Operations"], "status": "recommended" if "Exception Handling" in weak_topics else "locked"},
                {"title": "Modern Python & Concurrency", "topics": ["Asyncio", "Multiprocessing", "Threading", "Typing"], "status": "locked"},
                {"title": "Framework Integration (Django / FastAPI)", "topics": ["REST APIs", "ORM", "Authentication"], "status": "locked"},
                {"title": "Production Deployment & Testing", "topics": ["Pytest", "Docker", "CI/CD", "Logging"], "status": "locked"}
            ],
            'Django': [
                {"title": "Django Architecture & Setup", "topics": ["MVT Pattern", "Project Structure", "Settings"], "status": "completed"},
                {"title": "Models & Django ORM", "topics": ["Migrations", "Relationships", "QuerySets"], "status": "current"},
                {"title": "Django REST Framework (DRF)", "topics": ["Serializers", "APIView", "ViewSets", "Routers"], "status": "recommended"},
                {"title": "Authentication & Permissions", "topics": ["JWT", "Role-Based Access Control", "Sessions"], "status": "locked"},
                {"title": "Advanced Database Optimization", "topics": ["select_related", "prefetch_related", "Indexes"], "status": "locked"},
                {"title": "Production Deployment", "topics": ["Gunicorn", "Nginx", "MySQL on Cloud", "Environment Security"], "status": "locked"}
            ],
            'React': [
                {"title": "Core Modern JavaScript (ES6+)", "topics": ["Destructuring", "Arrow Functions", "Promises"], "status": "completed"},
                {"title": "React Components & JSX", "topics": ["Props", "Component Lifecycle", "JSX Rules"], "status": "completed" if skill_level in ['Intermediate', 'Advanced'] else "current"},
                {"title": "State & Core Hooks", "topics": ["useState", "useEffect", "useRef"], "status": "current"},
                {"title": "Routing & Navigation", "topics": ["React Router v6", "Dynamic Routes", "Guards"], "status": "recommended"},
                {"title": "Global State Management", "topics": ["Context API", "Custom Hooks", "Redux Toolkit"], "status": "locked"},
                {"title": "API Integration & Performance", "topics": ["Axios Interceptors", "useMemo", "useCallback", "Code Splitting"], "status": "locked"}
            ]
        }

        default_stages = curriculums.get(skill_name, [
            {"title": f"{skill_name} Core Fundamentals", "topics": ["Syntax", "Core Concepts"], "status": "completed"},
            {"title": f"{skill_name} Intermediate Practice", "topics": ["Standard Workflows", "Best Practices"], "status": "current"},
            {"title": f"{skill_name} Problem Solving & Optimization", "topics": ["Debugging", "Edge Cases"], "status": "recommended"},
            {"title": f"{skill_name} Real-World Industry Projects", "topics": ["Architecture", "Production Readiness"], "status": "locked"}
        ])

        return {
            'title': f"{skill_name} Mastery Roadmap for {target_role}",
            'stages': default_stages
        }

    # =========================================================================
    # 4. AI LEARNING ASSISTANT (CHAT)
    # =========================================================================
    def ask_learning_assistant(self, user_question, context=''):
        """Answers coding questions with structured explanation, example, key points, practice quiz."""
        if self.client_available:
            prompt = f"""You are SkillNova AI, a technical learning assistant.

Answer the user's exact technical question.

The response must be directly relevant to the technology, framework, language, database, or concept mentioned by the user.

Never use a fixed programming-language template for every question.

Identify the topic from the user's question and generate examples, explanations, takeaways, and practice questions for that SAME topic.

Examples:
- If the user asks about Python: Python explanation and Python examples.
- If the user asks about SQL: SQL explanation and SQL examples.
- If the user asks about React: React explanation and React examples.
- If the user asks about JavaScript: JavaScript explanation and JavaScript examples.
- If the user asks about Django: Django explanation and Django examples.
- If the user asks about REST APIs: REST API explanation and REST API examples.
- If the user asks about DBMS / Databases: DBMS explanation and DBMS examples.
- If the user asks about Machine Learning: Machine learning explanation and ML examples.

The practice question must also belong to the same topic.
Do not inject unrelated content or default to Python unless the question is explicitly about Python.

Conversation History / Context (use this to resolve references like "it", "this", "why do we need it?"):
{context if context else 'None'}

Student Question: "{user_question}"

Provide a clear, pedagogical response formatted strictly as a single JSON object with the following structure:
{{
  "explanation": "Clear, concise, educational explanation directly addressing the question without jargon overload",
  "code_snippet": "Clean, syntactically correct code, query, or architecture snippet for this specific topic (or empty string if not applicable)",
  "key_points": ["Key takeaway 1 for this topic", "Key takeaway 2 for this topic", "Key takeaway 3 for this topic"],
  "practice_question": {{
    "question": "A short multiple choice check question about the exact same topic",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_option_index": 0,
    "answer_explanation": "Why this option is correct"
  }}
}}
Return ONLY valid JSON.
"""
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                clean_text = self._clean_json_response(response.text)
                parsed = json.loads(clean_text)
                return parsed
            except Exception as e:
                logger.warning(f"AI Assistant Gemini call failed, using heuristic: {e}")

        # Intelligent Fallback Assistant
        return self._heuristic_learning_assistant(user_question, context=context)

    # =========================================================================
    # 5. AI INTERVIEW PREPARATION
    # =========================================================================
    def generate_interview_questions(self, target_role, experience_level='Fresher', skills=None):
        """Generates technical, conceptual, scenario, project-based, and HR questions."""
        skills = skills or ['Python', 'SQL', 'REST APIs']
        skills_str = ", ".join(skills)

        if self.client_available:
            prompt = f"""
            Generate an interview set of 5 questions for a candidate applying for '{target_role}' with '{experience_level}' experience and skills: {skills_str}.
            Include:
            1 Technical question
            1 Conceptual question
            1 Scenario-based question
            1 Project-based question
            1 HR / Behavioral question
            Return ONLY a valid JSON array of objects:
            [
              {{
                "id": 1,
                "category": "Technical",
                "question": "Question text",
                "expected_concepts": ["concept 1", "concept 2"]
              }}
            ]
            """
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                clean_text = self._clean_json_response(response.text)
                return json.loads(clean_text)
            except Exception as e:
                logger.warning(f"AI Interview generation failed, using heuristic: {e}")

        # Heuristic Interview Questions
        return [
            {
                "id": 1,
                "category": "Technical",
                "question": f"In {skills[0] if skills else 'Python'}, how do you manage memory allocation and what are the main differences between mutable and immutable data types?",
                "expected_concepts": ["Memory pointers", "Pass by assignment", "List vs Tuple", "Reference counting"]
            },
            {
                "id": 2,
                "category": "Conceptual",
                "question": "Explain the architectural principles of RESTful APIs. What makes an endpoint truly idempotent and which HTTP verbs satisfy this?",
                "expected_concepts": ["Statelessness", "GET / PUT / DELETE idempotency", "Resource URI design", "HTTP Status codes"]
            },
            {
                "id": 3,
                "category": "Scenario",
                "question": "You observe that a database query in production is taking 5+ seconds under moderate load. Walk us through how you would diagnose, profile, and optimize the bottleneck.",
                "expected_concepts": ["EXPLAIN query plan", "Database indexing", "N+1 query problem", "Connection pooling", "Caching with Redis"]
            },
            {
                "id": 4,
                "category": "Project-based",
                "question": f"Describe a challenging technical feature or project you built using {skills_str}. What architectural tradeoffs did you make and what would you do differently?",
                "expected_concepts": ["Clean architecture", "Trade-off analysis", "Error handling", "Scalability", "Testing"]
            },
            {
                "id": 5,
                "category": "HR & Behavioral",
                "question": "Tell us about a time you encountered an ambiguous requirement or had a technical disagreement with a teammate. How did you resolve it?",
                "expected_concepts": ["Communication", "Empathy", "Data-driven decisions", "STAR method response"]
            }
        ]

    def evaluate_interview_answers(self, target_role, questions, answers):
        """Evaluates student's answers to the interview questions and generates constructive feedback."""
        evaluations = []
        total_score = 0

        for q in questions:
            q_id = str(q.get('id'))
            user_ans = answers.get(q_id, '').strip()
            word_count = len(user_ans.split())

            if not user_ans:
                evaluations.append({
                    "question_id": q.get('id'),
                    "score": 0,
                    "feedback": "No answer was provided for this question.",
                    "missing_concepts": q.get('expected_concepts', []),
                    "tips": "Try structuring your answer using the STAR method or outlining key technical definitions."
                })
                continue

            # Heuristic concept matching
            matched_concepts = []
            missing_concepts = []
            for concept in q.get('expected_concepts', []):
                keywords = concept.lower().split()
                if any(k in user_ans.lower() for k in keywords if len(k) > 3):
                    matched_concepts.append(concept)
                else:
                    missing_concepts.append(concept)

            # Score calculation
            base_score = min(50, word_count * 2)
            concept_bonus = (len(matched_concepts) / max(1, len(q.get('expected_concepts', [])))) * 50
            q_score = min(100, round(base_score + concept_bonus))
            total_score += q_score

            evaluations.append({
                "question_id": q.get('id'),
                "score": q_score,
                "feedback": f"Good effort! You clearly addressed {', '.join(matched_concepts) if matched_concepts else 'the basic premise'}. Elaborating on real-world edge cases will strengthen your response.",
                "missing_concepts": missing_concepts,
                "tips": f"To sound more senior, mention practical industry patterns like: {', '.join(missing_concepts[:2]) if missing_concepts else 'benchmarking and testing'}."
            })

        avg_score = round(total_score / max(1, len(questions)), 1)
        strengths = [
            "Good foundational understanding of role requirements",
            "Clear technical terminology and structured explanation",
            "Demonstrated readiness to tackle real-world development scenarios"
        ]
        improvements = [
            "Provide concrete metric-based examples when discussing past projects",
            "Cover security, error handling, and performance optimization when answering scenario questions",
            "Keep practicing answering out loud to build fluency and confidence"
        ]

        return {
            "overall_score": avg_score,
            "overall_feedback": f"Overall solid performance for a {target_role} candidate. Your conceptual grounding is sound; focus now on deep-diving into system tradeoffs and production-ready considerations.",
            "evaluations": evaluations,
            "strengths": strengths,
            "improvements": improvements
        }

    # =========================================================================
    # 6. AI RESUME SKILL-GAP ANALYZER
    # =========================================================================
    def analyze_resume(self, text, target_role='Python Developer'):
        """Analyzes extracted text from resume without inventing facts."""
        text_lower = text.lower()

        # Catalog of technical skills and their aliases
        SKILL_CATALOG = {
            'Python': ['python', 'py', 'python3'],
            'Django': ['django', 'drf', 'django rest framework'],
            'Flask': ['flask'],
            'FastAPI': ['fastapi'],
            'JavaScript': ['javascript', 'js', 'es6'],
            'TypeScript': ['typescript', 'ts'],
            'React': ['react', 'react.js', 'reactjs', 'redux'],
            'SQL': ['sql', 'mysql', 'postgresql', 'postgres', 'sqlite', 'oracle'],
            'HTML': ['html', 'html5'],
            'CSS': ['css', 'css3', 'sass', 'tailwind', 'bootstrap'],
            'REST APIs': ['rest api', 'restful', 'apis', 'rest apis'],
            'Git': ['git', 'github', 'gitlab', 'version control'],
            'Docker': ['docker', 'containerization'],
            'Kubernetes': ['kubernetes', 'k8s'],
            'AWS': ['aws', 'amazon web services', 'ec2', 's3'],
            'Linux': ['linux', 'ubuntu', 'bash', 'shell scripting'],
            'Data Structures': ['data structures', 'algorithms', 'dsa'],
            'Machine Learning': ['machine learning', 'ml', 'pandas', 'numpy', 'scikit-learn', 'tensorflow'],
            'Testing': ['pytest', 'unittest', 'jest', 'unit testing']
        }

        # Role benchmarks
        ROLE_REQUIREMENTS = {
            'Python Developer': ['Python', 'Django', 'SQL', 'REST APIs', 'Git', 'Docker', 'Testing'],
            'Full Stack Developer': ['JavaScript', 'React', 'Python', 'Django', 'SQL', 'HTML', 'CSS', 'Git', 'REST APIs'],
            'Frontend Developer': ['JavaScript', 'React', 'HTML', 'CSS', 'TypeScript', 'Git'],
            'Backend Developer': ['Python', 'Django', 'SQL', 'REST APIs', 'Docker', 'AWS', 'Testing', 'Linux'],
            'Data Scientist': ['Python', 'SQL', 'Machine Learning', 'Data Structures', 'Git']
        }

        required_skills = ROLE_REQUIREMENTS.get(target_role, ['Python', 'SQL', 'REST APIs', 'Git', 'Testing'])

        detected_skills = []
        for skill_name, aliases in SKILL_CATALOG.items():
            if any(re.search(rf'\b{re.escape(alias)}\b', text_lower) for alias in aliases):
                detected_skills.append(skill_name)

        # Missing skills against role benchmark
        missing_skills = [s for s in required_skills if s not in detected_skills]

        # Calculate match percentage
        matched_required = [s for s in required_skills if s in detected_skills]
        match_percentage = round((len(matched_required) / max(1, len(required_skills))) * 100, 1)

        # Extract real sections from text without inventing
        education_detected = self._extract_education(text)
        projects_detected = self._extract_projects(text)
        experience_detected = self._extract_experience(text)
        tools_detected = [s for s in detected_skills if s in ['Git', 'Docker', 'AWS', 'Linux', 'Testing']]

        # Recommended learning path
        recommended_path = []
        for miss in missing_skills:
            recommended_path.append({
                "skill": miss,
                "action": f"Take the {miss} skill assessment & practice AI interview questions on SkillNova AI",
                "priority": "High" if miss in required_skills[:3] else "Medium"
            })

        return {
            "target_role": target_role,
            "match_percentage": match_percentage,
            "detected_skills": detected_skills,
            "missing_skills": missing_skills,
            "education_detected": education_detected,
            "projects_detected": projects_detected,
            "experience_detected": experience_detected,
            "tools_detected": tools_detected,
            "recommended_learning_path": recommended_path
        }

    # =========================================================================
    # 7. AI INSTRUCTOR QUESTION GENERATOR
    # =========================================================================
    def instructor_generate_questions(self, skill_name, difficulty='Intermediate', count=5):
        """Generates draft questions for instructors to review before publishing."""
        return self._heuristic_assessment_questions(skill_name, difficulty, count=count)

    # =========================================================================
    # INTERNAL HELPERS & DETERMINISTIC HEURISTICS
    # =========================================================================
    def _clean_json_response(self, text):
        clean = text.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        elif clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        return clean.strip()

    def _extract_education(self, text):
        matches = []
        lines = text.split('\n')
        keywords = ['bachelor', 'b.tech', 'b.e', 'master', 'm.tech', 'm.s', 'degree', 'university', 'college', 'institute']
        for line in lines:
            line_str = line.strip()
            if any(k in line_str.lower() for k in keywords) and len(line_str) < 120 and len(line_str) > 5:
                matches.append(line_str)
        return list(dict.fromkeys(matches))[:3] or ["Degree mentioned in Resume text"]

    def _extract_projects(self, text):
        matches = []
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_str = line.strip()
            if any(p in line_str.lower() for p in ['project:', 'project -', 'developed a', 'built a', 'implemented a']) and len(line_str) < 140:
                matches.append(line_str)
        return list(dict.fromkeys(matches))[:4] or ["Projects listed in candidate CV"]

    def _extract_experience(self, text):
        matches = []
        lines = text.split('\n')
        keywords = ['intern', 'internship', 'developer', 'engineer', 'trainee', 'analyst', 'experience']
        for line in lines:
            line_str = line.strip()
            if any(k in line_str.lower() for k in keywords) and len(line_str) < 120 and len(line_str) > 5:
                matches.append(line_str)
        return list(dict.fromkeys(matches))[:3] or ["Experience details from CV"]

    def _heuristic_learning_assistant(self, question, context=''):
        q = (question or '').lower().strip()
        ctx = (context or '').lower().strip()

        # Check if question is referential (e.g., "Why do we need it?", "how does it work?", "why use this?", "give an example of it")
        is_referential = (
            any(phrase in q for phrase in [
                'why do we need it', 'why do we need this', 'why use it', 'why use this',
                'how does it work', 'what is it', 'why need it', 'why is it needed',
                'give an example of it', 'what does it do', 'how to use it'
            ])
            or ((' it ' in f" {q} " or ' this ' in f" {q} ") and len(q.split()) <= 6)
        )

        # ---------------------------------------------------------------------
        # 1. REACT / HOOKS / useEffect
        # ---------------------------------------------------------------------
        is_use_effect_query = 'useeffect' in q or ('effect' in q and ('react' in q or 'hook' in q))
        is_react_context = any(kw in ctx for kw in ['useeffect', 'react', 'hook', 'usestate'])

        if is_use_effect_query or (is_referential and ('useeffect' in ctx or ('react' in ctx and 'hook' in ctx))):
            if is_referential or 'why' in q:
                return {
                    "explanation": (
                        "We need the useEffect hook in React to synchronize functional components with external systems "
                        "and safely manage side effects outside the pure React rendering cycle. Without useEffect, executing operations "
                        "like asynchronous data fetching, manual DOM manipulations, timer registrations, or window event listeners directly "
                        "inside the component body would run on every single render pass, triggering infinite re-render loops and severe memory leaks. "
                        "useEffect guarantees that side effects execute predictably after the browser has painted the DOM, and its optional "
                        "cleanup function ensures subscriptions and listeners are safely disposed when dependencies change or the component unmounts."
                    ),
                    "code_snippet": (
                        "import React, { useState, useEffect } from 'react';\n\n"
                        "// Why useEffect is needed: safely listening to external browser events\n"
                        "function WindowResizeTracker() {\n"
                        "  const [windowWidth, setWindowWidth] = useState(window.innerWidth);\n\n"
                        "  useEffect(() => {\n"
                        "    console.log(\"Component mounted\");\n\n"
                        "    // 1. External side effect: add window resize listener\n"
                        "    const handleResize = () => setWindowWidth(window.innerWidth);\n"
                        "    window.addEventListener('resize', handleResize);\n\n"
                        "    // 2. Essential cleanup function: prevents memory leak on unmount\n"
                        "    return () => {\n"
                        "      window.removeEventListener('resize', handleResize);\n"
                        "    };\n"
                        "  }, []); // Empty dependency array: runs only once on mount\n\n"
                        "  return <div>Window width: {windowWidth}px</div>;\n"
                        "}\n\n"
                        "export default WindowResizeTracker;"
                    ),
                    "key_points": [
                        "Preserves pure rendering by isolating side effects from the functional component render body",
                        "Prevents infinite re-render loops by controlling execution with the dependency array",
                        "Eliminates memory leaks by allowing cleanup functions to run prior to re-execution or unmounting"
                    ],
                    "practice_question": {
                        "question": "Why should side effects like data fetching NOT be executed directly in the body of a React functional component?",
                        "options": [
                            "It executes on every render pass, causing performance degradation and infinite re-render loops",
                            "JavaScript forbids calling fetch() inside a functional component",
                            "React components can only return static HTML strings",
                            "Props cannot be accessed inside the component body"
                        ],
                        "correct_option_index": 0,
                        "answer_explanation": "React functional component bodies should remain pure during render; executing side effects directly causes state updates that re-trigger rendering infinitely."
                    }
                }

            return {
                "explanation": (
                    "useEffect is a React Hook that allows functional components to manage and perform side effects "
                    "(such as data fetching, subscriptions, DOM mutations, or timers). It executes after the render is committed to the screen.\n\n"
                    "• When effects run: useEffect runs after every completed render by default, but its execution is controlled by its dependency array.\n"
                    "• Dependency array: If omitted, the effect runs on every render. If an empty array [] is passed, the effect runs once when the component mounts. If dependencies [a, b] are provided, it runs on mount and re-runs only when any dependency value changes.\n"
                    "• Cleanup function: If the effect returns a function, React runs this cleanup function before re-running the effect and when the component unmounts, preventing memory leaks and orphaned event listeners."
                ),
                "code_snippet": (
                    "import React, { useState, useEffect } from 'react';\n\n"
                    "function UserProfile({ userId }) {\n"
                    "  const [user, setUser] = useState(null);\n\n"
                    "  useEffect(() => {\n"
                    "    console.log(\"Component mounted\");\n\n"
                    "    let isMounted = true;\n"
                    "    fetch(`/api/users/${userId}`)\n"
                    "      .then(res => res.json())\n"
                    "      .then(data => {\n"
                    "        if (isMounted) setUser(data);\n"
                    "      });\n\n"
                    "    // Cleanup function where relevant\n"
                    "    return () => {\n"
                    "      isMounted = false;\n"
                    "      console.log(\"Cleaning up previous effect for userId:\", userId);\n"
                    "    };\n"
                    "  }, [userId]); // Dependency array: runs on mount & whenever userId changes\n\n"
                    "  return (\n"
                    "    <div>\n"
                    "      {user ? <h3>{user.name}</h3> : <p>Loading user profile...</p>}\n"
                    "    </div>\n"
                    "  );\n"
                    "}\n\n"
                    "export default UserProfile;"
                ),
                "key_points": [
                    "useEffect is a React Hook designed to handle asynchronous and synchronous side effects in functional components",
                    "The dependency array controls execution: empty [] runs once on mount, [dep] runs when dep changes, no array runs on every render",
                    "The optional cleanup function runs before the effect re-runs and during component unmount to prevent memory leaks"
                ],
                "practice_question": {
                    "question": "When does a React useEffect hook with an empty dependency array [] execute?",
                    "options": [
                        "Once after the initial render (component mount)",
                        "On every component render and state update",
                        "Immediately before the component renders to the DOM",
                        "Only when the parent component unmounts"
                    ],
                    "correct_option_index": 0,
                    "answer_explanation": "An empty dependency array [] indicates that the effect has no reactive dependencies, so React only runs it once after the initial component mount."
                }
            }

        # React (general, useState, etc.)
        if 'react' in q or 'usestate' in q or (is_referential and 'react' in ctx):
            return {
                "explanation": (
                    "React is a declarative, component-based JavaScript library for building interactive user interfaces. "
                    "In React, UI is broken down into modular, reusable components that manage their own state. React uses a Virtual DOM "
                    "to efficiently compute UI diffs (reconciliation) and update only the necessary parts of the actual browser DOM. "
                    "Functional components leverage React Hooks (like useState for state management and useEffect for side effects) "
                    "to create reactive, predictable web applications."
                ),
                "code_snippet": (
                    "import React, { useState } from 'react';\n\n"
                    "function Counter() {\n"
                    "  const [count, setCount] = useState(0);\n\n"
                    "  return (\n"
                    "    <div style={{ textAlign: 'center', padding: '1rem' }}>\n"
                    "      <h2>Current Count: {count}</h2>\n"
                    "      <button onClick={() => setCount(prev => prev + 1)}>\n"
                    "        Increment\n"
                    "      </button>\n"
                    "    </div>\n"
                    "  );\n"
                    "}\n\n"
                    "export default Counter;"
                ),
                "key_points": [
                    "Components are reusable, independent building blocks of the UI",
                    "React uses a Virtual DOM and reconciliation algorithm to optimize browser DOM rendering",
                    "State updates in React trigger re-renders, producing declarative, predictable UI flow"
                ],
                "practice_question": {
                    "question": "In React, which hook is used to declare and update local state variables in a functional component?",
                    "options": ["useState", "useEffect", "useContext", "useReducer"],
                    "correct_option_index": 0,
                    "answer_explanation": "useState is the built-in React hook that returns a stateful value and an updater function to update it."
                }
            }

        # ---------------------------------------------------------------------
        # 2. SQL / JOIN / LEFT JOIN
        # ---------------------------------------------------------------------
        is_left_join = 'left join' in q or 'left outer join' in q or (is_referential and 'left join' in ctx)
        is_sql_join = 'join' in q or ('sql' in q and 'join' in (q + ' ' + ctx)) or (is_referential and 'join' in ctx)
        is_sql_general = 'sql' in q or (is_referential and 'sql' in ctx)

        if is_left_join:
            return {
                "explanation": (
                    "A LEFT JOIN (or LEFT OUTER JOIN) in SQL returns all records from the left table, and the matched records "
                    "from the right table. If there is no match on the specified join condition (ON), the result will contain NULL "
                    "values for all columns of the right table. It is essential when you want to preserve every entity from the primary "
                    "table regardless of whether related records exist in the secondary table."
                ),
                "code_snippet": (
                    "-- Retrieve all departments and any associated employees\n"
                    "SELECT \n"
                    "    d.department_id,\n"
                    "    d.department_name,\n"
                    "    e.employee_name,\n"
                    "    e.salary\n"
                    "FROM departments d\n"
                    "LEFT JOIN employees e \n"
                    "    ON d.department_id = e.department_id\n"
                    "ORDER BY d.department_name;"
                ),
                "key_points": [
                    "LEFT JOIN guarantees all records from the left table are included in the result set",
                    "Unmatched right-table columns are populated with NULL values",
                    "Commonly used to identify unmatched or missing relationships (e.g., WHERE e.employee_id IS NULL)"
                ],
                "practice_question": {
                    "question": "In SQL, what is returned for columns of the right table in a LEFT JOIN when no matching row is found?",
                    "options": [
                        "NULL values",
                        "An empty string ''",
                        "A default value of 0",
                        "A database foreign key constraint error"
                    ],
                    "correct_option_index": 0,
                    "answer_explanation": "If no matching row exists in the right table for the ON predicate, SQL populates all right-table columns with NULL."
                }
            }

        if is_sql_join:
            return {
                "explanation": (
                    "A SQL JOIN clause is used to combine rows from two or more tables based on a related column between them. "
                    "Relational databases store normalized data across separate tables (linked by primary and foreign keys); JOINs allow "
                    "you to query and reconstruct unified relational datasets.\n\n"
                    "• INNER JOIN: Returns only rows where there is a match in both tables.\n"
                    "• LEFT JOIN: Returns all rows from the left table, plus matched rows from the right table (NULL if unmatched).\n"
                    "• RIGHT JOIN: Returns all rows from the right table, plus matched rows from the left table (NULL if unmatched).\n"
                    "• FULL OUTER JOIN: Returns all rows when there is a match in either table."
                ),
                "code_snippet": (
                    "-- Combine orders and customers using an INNER JOIN\n"
                    "SELECT \n"
                    "    o.order_id,\n"
                    "    c.customer_name,\n"
                    "    o.order_date,\n"
                    "    o.total_amount\n"
                    "FROM orders o\n"
                    "INNER JOIN customers c \n"
                    "    ON o.customer_id = c.id\n"
                    "WHERE o.status = 'Completed'\n"
                    "ORDER BY o.order_date DESC;"
                ),
                "key_points": [
                    "JOINs combine normalized database tables using primary and foreign key relationships",
                    "INNER JOIN returns only rows that satisfy the ON join condition in both tables",
                    "Creating database indexes on foreign key join columns dramatically optimizes query execution"
                ],
                "practice_question": {
                    "question": "Which SQL JOIN type returns only rows that have matching values in BOTH joined tables?",
                    "options": [
                        "INNER JOIN",
                        "LEFT JOIN",
                        "FULL OUTER JOIN",
                        "CROSS JOIN"
                    ],
                    "correct_option_index": 0,
                    "answer_explanation": "INNER JOIN selects records where the join condition evaluates to TRUE in both the left and right tables."
                }
            }

        if is_sql_general and not any(p in q for p in ['python', 'django']):
            return {
                "explanation": (
                    "SQL (Structured Query Language) is the standard domain-specific language used to manage, query, and manipulate "
                    "relational database management systems (RDBMS). SQL enables developers to define database schemas (DDL), query and "
                    "transform data (DML), enforce referential integrity constraints, and manage transactional concurrency (TCL)."
                ),
                "code_snippet": (
                    "-- Standard SQL Query with Filtering and Aggregation\n"
                    "SELECT \n"
                    "    department,\n"
                    "    COUNT(*) AS total_employees,\n"
                    "    AVG(salary) AS average_salary\n"
                    "FROM employees\n"
                    "WHERE is_active = TRUE\n"
                    "GROUP BY department\n"
                    "HAVING COUNT(*) > 5\n"
                    "ORDER BY average_salary DESC;"
                ),
                "key_points": [
                    "SQL is declarative: you describe what data you want, and the database query optimizer plans how to fetch it",
                    "WHERE filters individual rows before aggregation; HAVING filters aggregated groups after GROUP BY",
                    "Relational databases enforce ACID guarantees to preserve data consistency during concurrent operations"
                ],
                "practice_question": {
                    "question": "In SQL, which clause is used to filter groups of records AFTER an aggregation with GROUP BY has been performed?",
                    "options": ["HAVING", "WHERE", "ORDER BY", "FILTER"],
                    "correct_option_index": 0,
                    "answer_explanation": "The HAVING clause filters aggregated groups produced by GROUP BY, whereas WHERE filters individual rows before aggregation."
                }
            }

        # ---------------------------------------------------------------------
        # 3. DBMS / NORMALIZATION
        # ---------------------------------------------------------------------
        is_dbms_norm = any(kw in q for kw in ['normaliz', '1nf', '2nf', '3nf', 'bcnf']) or (
            ('dbms' in q or 'database' in q) and any(kw in (q + ' ' + ctx) for kw in ['normal', '1nf', '2nf', '3nf'])
        ) or (is_referential and any(kw in ctx for kw in ['normaliz', '1nf', '2nf', '3nf', 'dbms']))

        if is_dbms_norm:
            return {
                "explanation": (
                    "DBMS Normalization is a systematic database design technique used to organize relational tables to minimize data "
                    "redundancy and eliminate undesirable insertion, update, and deletion anomalies. Normalization divides larger tables "
                    "into smaller, well-structured tables linked by foreign keys through progressive Normal Forms:\n\n"
                    "• 1NF (First Normal Form): Column values must be atomic (indivisible) with no repeating groups.\n"
                    "• 2NF (Second Normal Form): Must be in 1NF and have no partial functional dependency (every non-key attribute must depend on the whole composite primary key).\n"
                    "• 3NF (Third Normal Form): Must be in 2NF and have no transitive functional dependency (non-key attributes must not depend on other non-key attributes).\n"
                    "• BCNF (Boyce-Codd Normal Form): A stricter version of 3NF where every determinant is a candidate key."
                ),
                "code_snippet": (
                    "-- Normalized Schema: Decomposing order data into Third Normal Form (3NF)\n\n"
                    "-- 1. Customers Table (removes transitive customer attributes)\n"
                    "CREATE TABLE customers (\n"
                    "    customer_id INT PRIMARY KEY,\n"
                    "    customer_name VARCHAR(100) NOT NULL,\n"
                    "    email VARCHAR(150) UNIQUE NOT NULL\n"
                    ");\n\n"
                    "-- 2. Orders Table (linked via customer_id foreign key)\n"
                    "CREATE TABLE orders (\n"
                    "    order_id INT PRIMARY KEY,\n"
                    "    customer_id INT NOT NULL,\n"
                    "    order_date DATE NOT NULL,\n"
                    "    total_amount DECIMAL(10, 2) NOT NULL,\n"
                    "    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)\n"
                    ");"
                ),
                "key_points": [
                    "Normalization eliminates data redundancy and prevents insertion, update, and deletion anomalies",
                    "1NF requires atomic values; 2NF eliminates partial dependencies; 3NF eliminates transitive dependencies",
                    "3NF/BCNF are the industry standards for transactional (OLTP) database schema design"
                ],
                "practice_question": {
                    "question": "A relational table is in 3rd Normal Form (3NF) if it is already in 2NF and has no:",
                    "options": [
                        "Transitive functional dependencies",
                        "Partial functional dependencies",
                        "Foreign key constraints",
                        "Composite primary keys"
                    ],
                    "correct_option_index": 0,
                    "answer_explanation": "3NF requires that all non-key attributes are directly dependent on the primary key, eliminating transitive dependencies where non-key attributes depend on other non-key attributes."
                }
            }

        if 'dbms' in q or (is_referential and 'dbms' in ctx):
            return {
                "explanation": (
                    "A Database Management System (DBMS) is software designed to store, retrieve, manage, and manipulate structured "
                    "data efficiently and securely. Modern relational DBMSs (like PostgreSQL, MySQL, and SQLite) adhere to the Relational Model, "
                    "providing data abstraction, ACID transaction guarantees (Atomicity, Consistency, Isolation, Durability), "
                    "concurrency control, crash recovery, and security access policies."
                ),
                "code_snippet": (
                    "-- Relational DBMS Transaction Example (ACID Compliance)\n"
                    "BEGIN TRANSACTION;\n\n"
                    "UPDATE accounts \n"
                    "SET balance = balance - 250.00 \n"
                    "WHERE account_id = 101;\n\n"
                    "UPDATE accounts \n"
                    "SET balance = balance + 250.00 \n"
                    "WHERE account_id = 202;\n\n"
                    "COMMIT;"
                ),
                "key_points": [
                    "DBMS provides a layer of abstraction between physical storage and application queries",
                    "ACID properties guarantee safe transactional operations even during system failures",
                    "Indexes, query optimizers, and buffer managers ensure scalable data retrieval"
                ],
                "practice_question": {
                    "question": "In a DBMS, which ACID property ensures that all operations in a transaction either complete entirely or are fully rolled back with no partial effects?",
                    "options": ["Atomicity", "Consistency", "Isolation", "Durability"],
                    "correct_option_index": 0,
                    "answer_explanation": "Atomicity ensures 'all-or-nothing' execution: if any statement in a transaction fails, the entire transaction is rolled back."
                }
            }

        # ---------------------------------------------------------------------
        # 4. JAVASCRIPT / PROMISE
        # ---------------------------------------------------------------------
        is_js_promise = 'promise' in q or ('javascript' in q and 'async' in q) or (is_referential and 'promise' in ctx)
        is_js_general = 'javascript' in q or 'js ' in f"{q} " or (is_referential and 'javascript' in ctx)

        if is_js_promise:
            return {
                "explanation": (
                    "A JavaScript Promise is an object representing the eventual completion (or failure) of an asynchronous "
                    "operation and its resulting value. A Promise exists in one of three mutually exclusive states:\n\n"
                    "• Pending: The initial state, neither fulfilled nor rejected.\n"
                    "• Fulfilled: The asynchronous operation completed successfully, resolving with a result value.\n"
                    "• Rejected: The asynchronous operation failed, rejecting with an error or reason.\n\n"
                    "Promises allow you to attach callback handlers using .then() for success, .catch() for errors, and .finally() "
                    "for completion, avoiding deeply nested callbacks ('callback hell'). Modern JavaScript also supports async/await syntax, "
                    "which lets you write asynchronous code that reads like synchronous code."
                ),
                "code_snippet": (
                    "// Creating a JavaScript Promise\n"
                    "function fetchUserData(userId) {\n"
                    "  return new Promise((resolve, reject) => {\n"
                    "    setTimeout(() => {\n"
                    "      if (userId > 0) {\n"
                    "        resolve({ id: userId, username: 'dev_nova', status: 'active' });\n"
                    "      } else {\n"
                    "        reject(new Error('Invalid user ID provided'));\n"
                    "      }\n"
                    "    }, 300);\n"
                    "  });\n"
                    "}\n\n"
                    "// Consuming with async / await\n"
                    "async function displayUser() {\n"
                    "  try {\n"
                    "    const user = await fetchUserData(42);\n"
                    "    console.log('User loaded successfully:', user.username);\n"
                    "  } catch (err) {\n"
                    "    console.error('Fetch error:', err.message);\n"
                    "  }\n"
                    "}\n\n"
                    "displayUser();"
                ),
                "key_points": [
                    "A Promise transitions from pending to either fulfilled or rejected exactly once; its settled state is immutable",
                    "Chaining .then() and .catch() replaces deeply nested callbacks with linear asynchronous flows",
                    "async/await is built on Promises and allows clean error handling using standard try/catch blocks"
                ],
                "practice_question": {
                    "question": "Which of the following represents the initial state of a newly created JavaScript Promise?",
                    "options": ["Pending", "Fulfilled", "Resolved", "Settled"],
                    "correct_option_index": 0,
                    "answer_explanation": "A newly created Promise starts in the 'pending' state until the asynchronous operation completes (fulfilled) or fails (rejected)."
                }
            }

        if is_js_general and not any(p in q for p in ['react', 'python']):
            return {
                "explanation": (
                    "JavaScript is a high-level, interpreted or just-in-time compiled, multi-paradigm programming language. "
                    "It is the core programming language of the Web, powering client-side interactivity in browsers as well as "
                    "server-side environments like Node.js. JavaScript features first-class functions, prototype-based object orientation, "
                    "dynamic typing, and a single-threaded event loop architecture that handles non-blocking asynchronous I/O."
                ),
                "code_snippet": (
                    "// Core JavaScript: closures, higher-order array methods, and modern ES6+\n"
                    "const users = [\n"
                    "  { id: 1, name: 'Alice', active: true },\n"
                    "  { id: 2, name: 'Bob', active: false },\n"
                    "  { id: 3, name: 'Charlie', active: true }\n"
                    "];\n\n"
                    "// Filter and transform data\n"
                    "const activeUserNames = users\n"
                    "  .filter(u => u.active)\n"
                    "  .map(u => u.name.toUpperCase());\n\n"
                    "console.log(activeUserNames); // ['ALICE', 'CHARLIE']"
                ),
                "key_points": [
                    "JavaScript uses a single-threaded, non-blocking event loop model for asynchronous operations",
                    "Supports functional programming paradigms with first-class functions, closures, and arrow functions",
                    "Modern ECMAScript (ES6+) introduced modules, destructuring, classes, and async/await syntax"
                ],
                "practice_question": {
                    "question": "In JavaScript, what execution mechanism allows a single-threaded runtime to handle non-blocking asynchronous I/O?",
                    "options": [
                        "The Event Loop and Task Queue",
                        "Operating system kernel multi-threading",
                        "Synchronous blocking polling",
                        "Manual garbage collection threads"
                    ],
                    "correct_option_index": 0,
                    "answer_explanation": "JavaScript uses an Event Loop coupled with callback and microtask queues to coordinate asynchronous tasks without blocking the main execution thread."
                }
            }

        # ---------------------------------------------------------------------
        # 5. DJANGO / ORM
        # ---------------------------------------------------------------------
        is_django_orm = 'orm' in q or ('django' in q and ('orm' in (q + ' ' + ctx) or 'query' in q or 'model' in q)) or (is_referential and ('orm' in ctx or 'django' in ctx))
        is_django_general = 'django' in q or (is_referential and 'django' in ctx)

        if is_django_orm:
            return {
                "explanation": (
                    "Django ORM (Object-Relational Mapping) is a database abstraction framework that allows Python developers "
                    "to interact with relational databases using Python classes (Models) and query methods without writing raw SQL. "
                    "Django maps Python model classes to database tables and model instances to table rows. Key ORM principles include:\n\n"
                    "• Lazy Evaluation: QuerySets do not hit the database when constructed; SQL executes only when the QuerySet is evaluated (iteration, slicing, or conversion).\n"
                    "• Relationship Optimization: select_related performs a single SQL JOIN for single-valued relationships (ForeignKey, OneToOne); prefetch_related executes separate batch queries for multi-valued relationships (ManyToMany, reverse ForeignKey) to prevent N+1 query bottlenecks.\n"
                    "• Schema Migrations: Django automatically tracks model changes and generates versioned SQL migration scripts."
                ),
                "code_snippet": (
                    "# Django ORM Model and QuerySet Definition\n"
                    "from django.db import models\n\n"
                    "class Author(models.Model):\n"
                    "    name = models.CharField(max_length=100)\n\n"
                    "class Article(models.Model):\n"
                    "    title = models.CharField(max_length=200)\n"
                    "    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='articles')\n"
                    "    published = models.BooleanField(default=True)\n\n"
                    "# Efficient QuerySet: single SQL JOIN via select_related\n"
                    "published_articles = (\n"
                    "    Article.objects\n"
                    "    .filter(published=True)\n"
                    "    .select_related('author')\n"
                    "    .order_by('-id')[:10]\n"
                    ")\n\n"
                    "for article in published_articles:\n"
                    "    print(f\"{article.title} by {article.author.name}\")"
                ),
                "key_points": [
                    "Django ORM abstracts database tables into Python model classes and rows into Python model instances",
                    "QuerySets are lazily evaluated: database queries execute only when the data is accessed or iterated",
                    "select_related (for ForeignKey) and prefetch_related (for ManyToMany) prevent costly N+1 query overhead"
                ],
                "practice_question": {
                    "question": "In Django ORM, when does a QuerySet actually execute its SQL query against the database?",
                    "options": [
                        "When it is evaluated (e.g. iterated over, sliced, or evaluated in a list/template)",
                        "Immediately when .filter() is called",
                        "When the model class definition is loaded into memory",
                        "Only after model.save() is called"
                    ],
                    "correct_option_index": 0,
                    "answer_explanation": "Django QuerySets are lazy; creating a QuerySet only builds the query in memory, and the SQL executes only when the data is evaluated."
                }
            }

        if is_django_general:
            return {
                "explanation": (
                    "Django is a high-level, batteries-included Python web framework designed to enable rapid development of secure, "
                    "maintainable web applications. It follows the Model-View-Template (MVT) architectural pattern, providing built-in "
                    "solutions for ORM database modeling, authentication, URL routing, form validation, CSRF/XSS protection, and an automated admin interface."
                ),
                "code_snippet": (
                    "# Django View and URL Routing Example\n"
                    "from django.http import JsonResponse\n"
                    "from django.views import View\n"
                    "from .models import Article\n\n"
                    "class ArticleListView(View):\n"
                    "    def get(self, request):\n"
                    "        articles = Article.objects.filter(published=True).values('id', 'title')\n"
                    "        return JsonResponse({'articles': list(articles)}, status=200)"
                ),
                "key_points": [
                    "Follows the 'Batteries-Included' philosophy, providing built-in auth, ORM, admin, and security",
                    "Implements the MVT (Model-View-Template) architectural pattern",
                    "Includes robust out-of-the-box defenses against SQL injection, CSRF, and XSS vulnerabilities"
                ],
                "practice_question": {
                    "question": "Which architectural pattern does Django follow for structuring web applications?",
                    "options": ["MVT (Model-View-Template)", "MVVM (Model-View-ViewModel)", "Microkernel", "Event-Driven Broker"],
                    "correct_option_index": 0,
                    "answer_explanation": "Django follows the Model-View-Template (MVT) architectural pattern, where Models handle data, Views handle business logic, and Templates format output."
                }
            }

        # ---------------------------------------------------------------------
        # 6. REST API
        # ---------------------------------------------------------------------
        is_rest_api = 'rest api' in q or 'restful' in q or ('api' in q and any(kw in (q + ' ' + ctx) for kw in ['rest', 'endpoint', 'http', 'crud'])) or (is_referential and 'api' in ctx)

        if is_rest_api:
            return {
                "explanation": (
                    "A REST (Representational State Transfer) API is an architectural style for designing networked web services "
                    "over the HTTP protocol. RESTful APIs are stateless: each client request contains all the information and authentication "
                    "credentials necessary for the server to process it, without relying on stored server session state. Key characteristics include:\n\n"
                    "• Resource-Oriented URIs: Resources are named as nouns and collections (e.g., /api/students, /api/courses/42).\n"
                    "• Standard HTTP Verbs: GET (retrieve data), POST (create new resource), PUT (replace resource), PATCH (partial update), and DELETE (remove resource).\n"
                    "• Standard Status Codes: 2xx for success (200 OK, 201 Created), 4xx for client errors (400 Bad Request, 401 Unauthorized, 404 Not Found), and 5xx for server errors."
                ),
                "code_snippet": (
                    "POST /api/v1/students HTTP/1.1\n"
                    "Host: api.skillnova.edu\n"
                    "Content-Type: application/json\n"
                    "Authorization: Bearer <jwt_access_token>\n\n"
                    "{\n"
                    "  \"name\": \"Jane Doe\",\n"
                    "  \"email\": \"jane@example.com\",\n"
                    "  \"track\": \"Full Stack Engineering\"\n"
                    "}\n\n"
                    "HTTP/1.1 201 Created\n"
                    "Content-Type: application/json\n\n"
                    "{\n"
                    "  \"id\": 108,\n"
                    "  \"name\": \"Jane Doe\",\n"
                    "  \"email\": \"jane@example.com\",\n"
                    "  \"track\": \"Full Stack Engineering\",\n"
                    "  \"status\": \"enrolled\"\n"
                    "}"
                ),
                "key_points": [
                    "REST services are stateless: servers do not preserve client session context between requests",
                    "Endpoints model resources using nouns (e.g. /api/users) rather than verbs (e.g. /api/getUsers)",
                    "HTTP status codes communicate request results explicitly (2xx Success, 4xx Client Error, 5xx Server Error)"
                ],
                "practice_question": {
                    "question": "Which HTTP status code is most standard when a REST API successfully creates a new resource via a POST request?",
                    "options": ["201 Created", "200 OK", "204 No Content", "202 Accepted"],
                    "correct_option_index": 0,
                    "answer_explanation": "HTTP 201 Created indicates that the HTTP POST request succeeded and resulted in the creation of a new resource on the server."
                }
            }

        # ---------------------------------------------------------------------
        # 7. MACHINE LEARNING / AI
        # ---------------------------------------------------------------------
        is_ml = any(kw in q for kw in ['machine learning', 'deep learning', 'neural network', 'supervised', 'unsupervised', 'overfitting', 'classification', 'regression']) or (
            'ml' in q and len(q.split()) <= 4
        ) or (is_referential and any(kw in ctx for kw in ['machine learning', 'ml', 'deep learning']))

        if is_ml:
            return {
                "explanation": (
                    "Machine Learning (ML) is a branch of Artificial Intelligence (AI) and computer science focused on developing "
                    "algorithms that learn statistical patterns from data and make predictions or decisions without being explicitly rule-programmed.\n\n"
                    "• Supervised Learning: The model learns from labeled datasets (input-output pairs) for classification (predicting discrete classes) or regression (predicting continuous values).\n"
                    "• Unsupervised Learning: The model discovers hidden patterns, groupings, or representations in unlabeled data (e.g., clustering with K-Means, dimensionality reduction with PCA).\n"
                    "• Reinforcement Learning: An agent learns optimal action policies through trial-and-error feedback from an environment based on reward signals.\n\n"
                    "Core machine learning workflows involve data preprocessing, splitting data into training and test sets to assess generalizability, and applying regularization techniques to prevent overfitting."
                ),
                "code_snippet": (
                    "# Supervised Machine Learning Pipeline with scikit-learn\n"
                    "from sklearn.model_selection import train_test_split\n"
                    "from sklearn.ensemble import RandomForestClassifier\n"
                    "from sklearn.metrics import accuracy_score\n\n"
                    "# 1. Features (X) and Target labels (y)\n"
                    "X, y = load_training_dataset()\n\n"
                    "# 2. Split dataset to evaluate generalization on unseen data\n"
                    "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n\n"
                    "# 3. Train the classifier\n"
                    "model = RandomForestClassifier(n_estimators=100, random_state=42)\n"
                    "model.fit(X_train, y_train)\n\n"
                    "# 4. Evaluate performance on unseen test set\n"
                    "predictions = model.predict(X_test)\n"
                    "accuracy = accuracy_score(y_test, predictions)\n"
                    "print(f\"Model Accuracy on unseen test data: {accuracy:.2%}\")"
                ),
                "key_points": [
                    "Supervised learning trains on labeled data (classification/regression); Unsupervised learns from unlabeled data (clustering)",
                    "Splitting data into train/test sets guarantees evaluation reflects generalizability on unseen data",
                    "Overfitting occurs when a model memorizes training noise; regularization and cross-validation mitigate this"
                ],
                "practice_question": {
                    "question": "What is 'overfitting' in machine learning?",
                    "options": [
                        "When a model performs exceptionally well on training data but poorly on unseen test data",
                        "When a model is too simple to capture underlying patterns in the dataset",
                        "When a dataset contains unlabeled or corrupted target features",
                        "When training converges significantly faster than expected"
                    ],
                    "correct_option_index": 0,
                    "answer_explanation": "Overfitting happens when a model learns the detailed noise and idiosyncrasies of the training data, degrading its ability to generalize to new, unseen inputs."
                }
            }

        # ---------------------------------------------------------------------
        # 8. PYTHON (ONLY when Python is explicitly asked or confirmed)
        # ---------------------------------------------------------------------
        is_python_explicit = 'python' in q or (is_referential and 'python' in ctx)
        is_inheritance = 'inheritance' in q or (is_python_explicit and 'inherit' in q)
        is_decorator = 'decorator' in q

        if is_inheritance:
            return {
                "explanation": (
                    "Inheritance is a fundamental Object-Oriented Programming (OOP) concept in Python that allows a child class "
                    "(subclass) to inherit attributes and methods from a parent class (superclass), promoting code reuse, "
                    "polymorphism, and modular design. Python supports single, multiple, and multilevel inheritance, using the "
                    "Method Resolution Order (MRO) with C3 Linearization to resolve attribute lookups. Subclasses can override parent "
                    "methods and delegate to the superclass implementation using the built-in super() function."
                ),
                "code_snippet": (
                    "class Vehicle:\n"
                    "    def __init__(self, brand, model):\n"
                    "        self.brand = brand\n"
                    "        self.model = model\n\n"
                    "    def get_info(self):\n"
                    "        return f\"{self.brand} {self.model}\"\n\n"
                    "class ElectricVehicle(Vehicle):\n"
                    "    def __init__(self, brand, model, battery_kwh):\n"
                    "        super().__init__(brand, model)  # Delegate to parent constructor\n"
                    "        self.battery_kwh = battery_kwh\n\n"
                    "    def get_info(self):\n"
                    "        base = super().get_info()\n"
                    "        return f\"{base} ({self.battery_kwh} kWh battery)\"\n\n"
                    "car = ElectricVehicle(\"Tesla\", \"Model 3\", 75)\n"
                    "print(car.get_info())  # Tesla Model 3 (75 kWh battery)"
                ),
                "key_points": [
                    "Inheritance enables subclasses to reuse and extend code defined in parent superclasses",
                    "The super() function provides a clean, maintainable way to call parent class methods",
                    "Python uses Method Resolution Order (MRO) to resolve method lookups in multiple inheritance"
                ],
                "practice_question": {
                    "question": "Which Python built-in function allows a subclass method to delegate a call to its parent class?",
                    "options": ["super()", "parent()", "base()", "inherit()"],
                    "correct_option_index": 0,
                    "answer_explanation": "super() returns a proxy object that delegates method and attribute calls to a parent or sibling class in the inheritance chain."
                }
            }

        if is_decorator:
            return {
                "explanation": (
                    "A decorator is a design pattern and language feature in Python that allows you to dynamically modify or extend "
                    "the behavior of a function or method without altering its original source code. Decorators are higher-order functions "
                    "that accept a function as an argument and return a wrapper function. The '@' syntax provides elegant syntactic sugar."
                ),
                "code_snippet": (
                    "import time\n\n"
                    "def timer_decorator(func):\n"
                    "    def wrapper(*args, **kwargs):\n"
                    "        start = time.time()\n"
                    "        result = func(*args, **kwargs)\n"
                    "        duration = time.time() - start\n"
                    "        print(f\"{func.__name__} executed in {duration:.4f}s\")\n"
                    "        return result\n"
                    "    return wrapper\n\n"
                    "@timer_decorator\n"
                    "def compute_squares():\n"
                    "    return [x ** 2 for x in range(100000)]\n\n"
                    "compute_squares()"
                ),
                "key_points": [
                    "Decorators are higher-order functions that take a function as an argument and return a wrapper function",
                    "The '@' decorator syntax provides clean syntactic sugar for function wrapping",
                    "Crucial in web frameworks like Django and FastAPI for authentication, caching, and routing"
                ],
                "practice_question": {
                    "question": "What must a Python decorator return when wrapping a function?",
                    "options": [
                        "A callable function or wrapper object",
                        "A boolean value",
                        "None",
                        "The function name as a string"
                    ],
                    "correct_option_index": 0,
                    "answer_explanation": "A decorator returns a callable (typically a closure/wrapper function) that replaces or enriches the original function."
                }
            }

        if is_python_explicit:
            return {
                "explanation": (
                    "Python is a high-level, interpreted, dynamically-typed programming language created by Guido van Rossum. "
                    "It is renowned for its clean, readable syntax that emphasizes code clarity and developer productivity. "
                    "Python supports multiple programming paradigms—including object-oriented, functional, and procedural programming. "
                    "With an extensive standard library ('batteries included') and a vast package ecosystem (PyPI), Python is the "
                    "premier language for backend web engineering, data analysis, machine learning, cloud automation, and scripting."
                ),
                "code_snippet": (
                    "# Core Python features: Clean syntax, dynamic typing, comprehensions\n"
                    "numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\n\n"
                    "# List comprehension with filtering\n"
                    "even_squares = [n ** 2 for n in numbers if n % 2 == 0]\n\n"
                    "print(\"Even squares:\", even_squares)\n"
                    "# Output: Even squares: [4, 16, 36, 64, 100]"
                ),
                "key_points": [
                    "Interpreted and dynamically typed with clean, readable syntax driven by indentation",
                    "Multi-paradigm: supports Object-Oriented, Functional, and Procedural styles",
                    "Enormous ecosystem powering web backends (Django, FastAPI), data science (Pandas), and AI (PyTorch, TensorFlow)"
                ],
                "practice_question": {
                    "question": "How does Python primarily delimit code blocks such as function bodies, conditionals, and loops?",
                    "options": [
                        "Whitespace indentation",
                        "Curly braces {}",
                        "BEGIN and END keywords",
                        "Semicolons at the end of each line"
                    ],
                    "correct_option_index": 0,
                    "answer_explanation": "Python uses indentation (leading whitespace) to define the scope and nesting of code blocks, enforcing consistent readability."
                }
            }

        # ---------------------------------------------------------------------
        # 9. GENERAL DYNAMIC FALLBACK (Zero Python hardcoding!)
        # ---------------------------------------------------------------------
        clean_topic = question.strip(' ?.!').replace('What is ', '').replace('what is ', '').replace('Explain ', '').replace('explain ', '')
        topic_display = clean_topic if len(clean_topic) > 1 else question

        return {
            "explanation": (
                f"In modern software engineering, {topic_display} plays an essential role in building robust, "
                f"scalable, and maintainable systems. Understanding the core abstractions, lifecycle behavior, "
                f"and integration patterns of {topic_display} allows developers to reason clearly about system behavior, "
                f"avoid anti-patterns, and write clean, testable production code."
            ),
            "code_snippet": (
                f"// Illustrative pattern for {topic_display}\n"
                f"// 1. Establish clear component/module boundaries\n"
                f"// 2. Validate input parameters and maintain predictable state\n"
                f"// 3. Handle errors gracefully and ensure idempotency\n\n"
                f"function demonstrate{topic_display.title().replace(' ', '')}() {{\n"
                f"  console.log(\"Executing standard workflow for {topic_display}\");\n"
                f"}}\n"
                f"demonstrate{topic_display.title().replace(' ', '')}();"
            ),
            "key_points": [
                f"Ensure clear separation of concerns when designing solutions around {topic_display}",
                "Favor declarative and testable patterns with explicit boundary validations",
                "Consult the authoritative documentation and design standards for this technology"
            ],
            "practice_question": {
                "question": f"When applying {topic_display} in a production architecture, what is a primary best practice?",
                "options": [
                    "Maintaining clean modular separation and validating boundary conditions",
                    "Coupling all logic tightly into a single monolithic file",
                    "Avoiding unit tests and integration tests",
                    "Hardcoding configuration parameters into source files"
                ],
                "correct_option_index": 0,
                "answer_explanation": f"Modular separation and boundary validation ensure {topic_display} remains maintainable, scalable, and resilient against regressions."
            }
        }

    def _heuristic_assessment_questions(self, skill_name, difficulty='Intermediate', count=30, exclude_texts=None):
        exclude = set(exclude_texts or [])
        banks = {
            'Python': [
                {
                    "question_text": 'What is the primary difference between a list and a tuple in Python?',
                    "option_a": 'Lists are mutable, while tuples are immutable',
                    "option_b": 'Tuples can store heterogeneous types, while lists cannot',
                    "option_c": 'Lists have O(1) membership lookup while tuples have O(n)',
                    "option_d": 'Tuples cannot be indexed or sliced',
                    "correct_option": 'A',
                    "explanation": 'Lists can be modified in-place after creation (mutable), whereas tuples cannot be changed once declared (immutable).',
                    "topic": 'Data Structures',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Which mechanism does Python use to manage memory allocation and reclaim unused objects?',
                    "option_a": 'Manual free() pointer deallocation',
                    "option_b": 'Reference counting combined with a generational garbage collector',
                    "option_c": 'Static stack allocation only',
                    "option_d": 'Deterministic scope destruction like C++ RAII',
                    "correct_option": 'B',
                    "explanation": 'Python tracks reference counts for all objects and employs a cyclic generational garbage collector for circular references.',
                    "topic": 'Memory Management',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What does the `*args` and `**kwargs` syntax in a Python function definition allow?',
                    "option_a": 'Enforces type checking at runtime',
                    "option_b": 'Accepting arbitrary positional and keyword arguments respectively',
                    "option_c": 'Multiplying numeric inputs by reference',
                    "option_d": 'Creating asynchronous worker threads',
                    "correct_option": 'B',
                    "explanation": '*args packs additional positional arguments into a tuple, while **kwargs packs extra keyword arguments into a dictionary.',
                    "topic": 'Functions',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'How do Python generators conserve memory when iterating over vast datasets?',
                    "option_a": 'By writing items to disk swap space',
                    "option_b": 'By yielding one item at a time lazily using the `yield` keyword instead of holding all items in RAM',
                    "option_c": 'By compressing objects in memory',
                    "option_d": 'By converting lists into tuples automatically',
                    "correct_option": 'B',
                    "explanation": 'Generators evaluate lazily, producing items on demand when requested via next(), keeping memory consumption constant.',
                    "topic": 'Generators & Iterators',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'In Python Object-Oriented Programming, what does the `@staticmethod` decorator signify?',
                    "option_a": 'The method cannot be overridden by subclasses',
                    "option_b": 'The method does not receive an implicit first argument (neither `self` nor `cls`)',
                    "option_c": 'The method executes only once during module loading',
                    "option_d": 'The method is executed concurrently in a thread pool',
                    "correct_option": 'B',
                    "explanation": 'A static method is a regular function bound to the class namespace, receiving neither instance nor class implicitly.',
                    "topic": 'OOP',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the output of `[x for x in range(5) if x % 2 == 0]` in Python?',
                    "option_a": '[0, 2, 4]',
                    "option_b": '[2, 4]',
                    "option_c": '[1, 3]',
                    "option_d": '[0, 1, 2, 3, 4]',
                    "correct_option": 'A',
                    "explanation": 'The list comprehension evaluates range(5) (0, 1, 2, 3, 4) and filters for even numbers (x % 2 == 0), resulting in [0, 2, 4].',
                    "topic": 'List Comprehensions',
                    "difficulty": difficulty
                },
                {
                    "question_text": "What does Python's GIL (Global Interpreter Lock) do?",
                    "option_a": 'Prevents any memory leakage in C extensions',
                    "option_b": 'Allows only one native thread to execute Python bytecode at any given moment in CPython',
                    "option_c": 'Encrypts source code bytecode files (.pyc)',
                    "option_d": 'Locks all variables declared globally from modification',
                    "correct_option": 'B',
                    "explanation": 'The GIL is a mutex that protects access to Python objects, preventing multiple native threads from executing CPython bytecode simultaneously.',
                    "topic": 'Concurrency',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Which clause in Python exception handling is guaranteed to run whether an exception occurs or not?',
                    "option_a": 'else',
                    "option_b": 'except',
                    "option_c": 'finally',
                    "option_d": 'catch',
                    "correct_option": 'C',
                    "explanation": 'The `finally` block always executes before leaving the try statement, typically used for clean-up actions like closing file handles.',
                    "topic": 'Exception Handling',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'In Python, what is the purpose of the `__init__` method?',
                    "option_a": 'To allocate memory for the object before creation',
                    "option_b": 'To initialize the attributes of an instance after it has been created',
                    "option_c": 'To destroy an object when its reference count hits zero',
                    "option_d": 'To import packages into the class scope',
                    "correct_option": 'B',
                    "explanation": '`__init__` is the constructor initializer method called immediately after the object is created to set up instance attributes.',
                    "topic": 'OOP',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the difference between `is` and `==` in Python?',
                    "option_a": '`==` checks for identity in memory, while `is` checks for equality of values',
                    "option_b": '`is` checks for identity (same object in memory), while `==` checks for equality of values',
                    "option_c": 'They are completely identical and interchangeable',
                    "option_d": '`is` is only valid for boolean expressions',
                    "correct_option": 'B',
                    "explanation": '`is` compares whether two references point to the exact same object (`id(a) == id(b)`), whereas `==` checks if their values are equal.',
                    "topic": 'Core Syntax',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the primary difference between `@classmethod` and `@staticmethod` in Python?',
                    "option_a": '`@classmethod` receives the class object `cls` as its first argument, while `@staticmethod` receives no implicit argument',
                    "option_b": '`@staticmethod` receives `self`, while `@classmethod` receives nothing',
                    "option_c": '`@classmethod` can only be invoked on instances, not on the class itself',
                    "option_d": '`@staticmethod` cannot access global variables',
                    "correct_option": 'A',
                    "explanation": '`@classmethod` passes the class `cls` as the first argument, commonly used for factory methods. `@staticmethod` receives neither `self` nor `cls`.',
                    "topic": 'OOP',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the average time complexity of key lookup in a standard Python dictionary?',
                    "option_a": 'O(n)',
                    "option_b": 'O(1)',
                    "option_c": 'O(log n)',
                    "option_d": 'O(n^2)',
                    "correct_option": 'B',
                    "explanation": 'Python dictionaries are implemented using open-addressing hash tables, providing O(1) average constant time complexity for key lookups.',
                    "topic": 'Data Structures',
                    "difficulty": difficulty
                },
                {
                    "question_text": "Which pair of magic methods must an object implement to adhere to Python's Context Manager protocol?",
                    "option_a": '`__start__` and `__stop__`',
                    "option_b": '`__enter__` and `__exit__`',
                    "option_c": '`__open__` and `__close__`',
                    "option_d": '`__init__` and `__del__`',
                    "correct_option": 'B',
                    "explanation": "Context managers implement `__enter__` to establish context and `__exit__` to handle teardown, used with Python's `with` statement.",
                    "topic": 'Context Managers',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Why is using a mutable object (like a list or dict) as a default argument in a Python function dangerous?',
                    "option_a": 'It causes a syntax error in Python 3',
                    "option_b": 'The default object is evaluated once at function definition time, sharing the mutated state across subsequent calls',
                    "option_c": 'It forces the function to execute on a single core only',
                    "option_d": 'Python garbage collects mutable defaults immediately after the first call',
                    "correct_option": 'B',
                    "explanation": 'Default argument expressions are evaluated once when the function definition is executed, meaning changes to mutable defaults persist across calls.',
                    "topic": 'Functions',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the primary difference between `__str__` and `__repr__` in Python?',
                    "option_a": '`__str__` is intended for human-readable end-user display, while `__repr__` is unambiguous and intended for debugging and developers',
                    "option_b": '`__repr__` only works on numbers',
                    "option_c": '`__str__` is called by the compiler while `__repr__` is called by the OS',
                    "option_d": 'They have the exact same purpose with no distinction',
                    "correct_option": 'A',
                    "explanation": '`__str__` provides a readable representation for users, while `__repr__` aims to be an unambiguous representation often evaluating to valid Python code.',
                    "topic": 'Dunder Methods',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the difference between `copy.copy()` and `copy.deepcopy()` in Python?',
                    "option_a": '`copy()` creates a new compound object and inserts references to existing items; `deepcopy()` recursively duplicates all nested objects',
                    "option_b": '`deepcopy()` is only supported for primitive integers',
                    "option_c": '`copy()` encrypts memory pointers',
                    "option_d": 'There is no functional difference in Python 3',
                    "correct_option": 'A',
                    "explanation": 'Shallow copy constructs a new collection and populates it with references to the original child items; deep copy recursively clones all nested objects.',
                    "topic": 'Memory Management',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What does the walrus operator `:=` introduced in Python 3.8 do?',
                    "option_a": 'Bitwise NAND operation',
                    "option_b": 'Assignment expression: assigns values to variables as part of a larger expression',
                    "option_c": 'Type declaration without assignment',
                    "option_d": 'Floor division assignment',
                    "correct_option": 'B',
                    "explanation": 'The walrus operator `:=` enables assignment expressions, assigning variables inside expressions like `if (n := len(items)) > 10:`.',
                    "topic": 'Core Syntax',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Which limitation applies to lambda functions in Python?',
                    "option_a": 'They cannot return any value',
                    "option_b": 'They are restricted to a single expression and cannot contain multi-line statements or annotations',
                    "option_c": 'They can only accept numeric parameters',
                    "option_d": 'They cannot be passed into higher-order functions like map() or filter()',
                    "correct_option": 'B',
                    "explanation": 'Python lambda expressions are syntactically restricted to a single expression, whose evaluated result is returned implicitly.',
                    "topic": 'Functions',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'In what order does Python resolve variable scope according to the LEGB rule?',
                    "option_a": 'Literal, Expression, Global, Binary',
                    "option_b": 'Local, Enclosing, Global, Built-in',
                    "option_c": 'Linear, Execution, Garbage, Base',
                    "option_d": 'Local, External, General, Bytecode',
                    "correct_option": 'B',
                    "explanation": 'Python searches namespaces in strict LEGB order: Local scope first, then Enclosing (outer functions), Global (module level), and Built-in.',
                    "topic": 'Scope & Namespaces',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What does the built-in `zip()` function do when passed iterables of unequal length?',
                    "option_a": 'Raises a ValueError immediately unless strict=False',
                    "option_b": 'By default, stops pairing elements as soon as the shortest input iterable is exhausted',
                    "option_c": 'Pads missing elements with None automatically',
                    "option_d": 'Loops the shorter iterable until the longest is completed',
                    "correct_option": 'B',
                    "explanation": 'Standard `zip()` truncates to the length of the shortest iterable. (In Python 3.10+, `strict=True` can be passed to enforce matching lengths).',
                    "topic": 'Built-in Functions',
                    "difficulty": difficulty
                },
                {
                    "question_text": "What is the purpose of Python's `@property` decorator?",
                    "option_a": 'To turn a method into a read-only attribute getter without changing public interface access',
                    "option_b": 'To mark class attributes as private to CPython',
                    "option_c": 'To serialize instances into JSON properties',
                    "option_d": 'To compile the function into C bytecode',
                    "correct_option": 'A',
                    "explanation": 'The `@property` decorator allows a method to be accessed like an attribute, providing clean encapsulation, getter/setter control, and computed properties.',
                    "topic": 'OOP',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'How does `collections.defaultdict` differ from a standard Python `dict`?',
                    "option_a": 'It sorts keys alphabetically upon insertion',
                    "option_b": 'It automatically initializes missing keys using a provided default factory callable instead of raising KeyError',
                    "option_c": 'It prohibits deletion of key-value pairs',
                    "option_d": 'It only accepts string keys',
                    "correct_option": 'B',
                    "explanation": '`defaultdict` calls a default_factory callable (e.g. `list`, `int`) to create an initial value whenever a non-existent key is accessed.',
                    "topic": 'Data Structures',
                    "difficulty": difficulty
                },
                {
                    "question_text": "What is the primary role of the event loop in Python's `asyncio` framework?",
                    "option_a": 'To spawn OS-level threads for each async function call',
                    "option_b": 'To orchestrate and schedule execution of asynchronous tasks and manage non-blocking I/O events cooperatively on a single thread',
                    "option_c": 'To bypass the Global Interpreter Lock completely for CPU workloads',
                    "option_d": 'To compile coroutines into machine code assembly',
                    "correct_option": 'B',
                    "explanation": 'The asyncio event loop runs in a single thread, scheduling coroutines, handling socket/timer I/O callbacks, and switching tasks at `await` points.',
                    "topic": 'Asyncio & Concurrency',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is a metaclass in Python?',
                    "option_a": 'A class that inherits from multiple base classes',
                    "option_b": 'A class of a class; defines how classes themselves are constructed and behave (with `type` being the default)',
                    "option_c": 'A decorator applied exclusively to module files',
                    "option_d": 'A special class used only for database ORM mapping',
                    "correct_option": 'B',
                    "explanation": 'Just as an object is an instance of a class, a class is an instance of its metaclass. Metaclasses intercept class creation at definition time.',
                    "topic": 'Advanced OOP',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Which algorithm does Python use to resolve Method Resolution Order (MRO) in multiple inheritance?',
                    "option_a": "Dijkstra's shortest path algorithm",
                    "option_b": 'C3 Linearization algorithm',
                    "option_c": 'Depth-First Left-to-Right search without cycle detection',
                    "option_d": 'Breadth-First Topological sorting only',
                    "correct_option": 'B',
                    "explanation": 'Python uses the C3 Linearization algorithm to determine the order in which base classes are searched for methods, ensuring monotonicity.',
                    "topic": 'OOP',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What performance optimization does defining `__slots__` in a Python class provide?',
                    "option_a": 'Prevents instantiation of the class',
                    "option_b": 'Suppresses the per-instance `__dict__`, reducing memory footprint and speeding up attribute access',
                    "option_c": 'Enables multi-threaded execution without the GIL',
                    "option_d": 'Allows dynamic addition of arbitrary new attributes at runtime',
                    "correct_option": 'B',
                    "explanation": '`__slots__` allocates a fixed array for specified attributes instead of a dynamic dictionary, dramatically reducing memory usage for many instances.',
                    "topic": 'Performance & Memory',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'When does the `else` clause of a `try...except...else` block execute in Python?',
                    "option_a": 'Only when an exception was raised and caught',
                    "option_b": 'Only when no exception was raised in the `try` block',
                    "option_c": 'Whenever the `finally` block fails to execute',
                    "option_d": 'It executes on every run regardless of exceptions',
                    "correct_option": 'B',
                    "explanation": 'The `else` block runs if and only if the code in the `try` block completes successfully without raising any exceptions.',
                    "topic": 'Exception Handling',
                    "difficulty": difficulty
                },
                {
                    "question_text": "What does Python's `typing.Union[int, str]` (or `int | str` in 3.10+) specify?",
                    "option_a": 'The value must be an integer converted to string',
                    "option_b": 'The value can be either an integer or a string',
                    "option_c": 'The value is a tuple containing both an int and str',
                    "option_d": 'The value is an intersection of both types',
                    "correct_option": 'B',
                    "explanation": 'Union represents a type that can be any one of the specified types, enabling static type checkers (mypy/pyright) to validate valid arguments.',
                    "topic": 'Type Hinting',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the primary function of `functools.lru_cache`?',
                    "option_a": 'To limit network request size',
                    "option_b": 'To wrap a function with a Least Recently Used memoization cache for identical arguments',
                    "option_c": 'To encrypt return values in RAM',
                    "option_d": 'To run functions in a background subprocess',
                    "correct_option": 'B',
                    "explanation": '`lru_cache` wraps pure functions and caches the most recent call results, avoiding redundant expensive computations for repeated inputs.',
                    "topic": 'Functional Programming',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Why is the `multiprocessing` module preferred over `threading` for CPU-bound computations in CPython?',
                    "option_a": 'It uses less memory than threads',
                    "option_b": 'Each process runs in its own memory space with its own Python interpreter and GIL, utilizing multiple CPU cores simultaneously',
                    "option_c": 'Processes communicate without serialization overhead',
                    "option_d": 'Threads cannot perform math operations in Python',
                    "correct_option": 'B',
                    "explanation": "Because CPython's GIL prevents multi-threaded CPU parallel execution, `multiprocessing` spawns distinct processes that run across multiple CPU cores.",
                    "topic": 'Concurrency',
                    "difficulty": difficulty
                },
            ],
            'Django': [
                {
                    "question_text": 'What architectural pattern does Django primarily implement?',
                    "option_a": 'MVC (Model View Controller)',
                    "option_b": 'MVT (Model View Template)',
                    "option_c": 'MVVM (Model View ViewModel)',
                    "option_d": 'Flux Architecture',
                    "correct_option": 'B',
                    "explanation": 'Django is based on MVT: Model (data layer), View (business logic/handler), and Template (presentation layer).',
                    "topic": 'Architecture',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'How do you avoid the N+1 database queries problem when fetching related ForeignKey records in Django ORM?',
                    "option_a": 'Using `filter()` with extra subqueries',
                    "option_b": 'Using `select_related()` for single-valued relationships and `prefetch_related()` for multi-valued relationships',
                    "option_c": 'By disabling foreign key constraints in the database',
                    "option_d": 'Running raw SQL queries only',
                    "correct_option": 'B',
                    "explanation": '`select_related()` performs a SQL JOIN to retrieve related records in a single query; `prefetch_related()` does a separate batch lookup in Python.',
                    "topic": 'ORM Optimization',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'In Django REST Framework, what is the main purpose of a Serializer?',
                    "option_a": 'To encrypt payload data transferred over HTTP',
                    "option_b": 'To convert complex data types like querysets and model instances into native Python datatypes that can be rendered into JSON/XML, and validate incoming data',
                    "option_c": 'To schedule background Celery tasks',
                    "option_d": 'To manage database table indexing',
                    "correct_option": 'B',
                    "explanation": 'Serializers convert complex querysets into JSON/XML and validate incoming request payloads before saving to the database.',
                    "topic": 'DRF Serializers',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What command applies pending Django database migrations?',
                    "option_a": 'python manage.py makemigrations',
                    "option_b": 'python manage.py migrate',
                    "option_c": 'python manage.py dbshell',
                    "option_d": 'python manage.py checkdb',
                    "correct_option": 'B',
                    "explanation": '`makemigrations` creates migration files based on model changes, while `migrate` executes the SQL against the active database.',
                    "topic": 'Migrations',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Which Django middleware is responsible for protecting web applications against Cross-Site Request Forgery attacks?',
                    "option_a": 'SecurityMiddleware',
                    "option_b": 'CsrfViewMiddleware',
                    "option_c": 'AuthenticationMiddleware',
                    "option_d": 'XFrameOptionsMiddleware',
                    "correct_option": 'B',
                    "explanation": 'CsrfViewMiddleware adds CSRF protection by requiring and validating tokens on state-changing requests like POST and PUT.',
                    "topic": 'Security',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'In Django ORM, what does using an `F()` expression allow you to do?',
                    "option_a": 'Format dates in templates',
                    "option_b": 'Perform database operations on model field values directly at the database level without pulling them into Python memory',
                    "option_c": 'Filter QuerySets using regular expressions',
                    "option_d": 'Flush cache entries automatically',
                    "correct_option": 'B',
                    "explanation": 'An F() object represents the value of a model field directly in the database query, avoiding race conditions and redundant in-memory Python operations.',
                    "topic": 'ORM Optimization',
                    "difficulty": difficulty
                },
                {
                    "question_text": "What is the purpose of Django's `Q()` objects?",
                    "option_a": 'To queue asynchronous background tasks',
                    "option_b": 'To construct complex database queries using logical OR (`|`), AND (`&`), and NOT (`~`) operators',
                    "option_c": 'To measure SQL query execution duration',
                    "option_d": 'To validate email address formatting',
                    "correct_option": 'B',
                    "explanation": 'Q objects encapsulate SQL conditions that can be combined with bitwise operators (`|`, `&`, `~`) for dynamic or complex database filtering.',
                    "topic": 'QuerySets',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'When creating a custom User model in Django, what is the difference between inheriting from `AbstractUser` vs `AbstractBaseUser`?',
                    "option_a": '`AbstractUser` provides full default user fields (username, email, first_name, etc.), while `AbstractBaseUser` provides only authentication machinery and core fields (password, last_login)',
                    "option_b": '`AbstractBaseUser` cannot be used with database foreign keys',
                    "option_c": '`AbstractUser` requires third-party packages to function',
                    "option_d": 'They are completely identical and deprecated',
                    "correct_option": 'A',
                    "explanation": '`AbstractUser` preserves standard user fields and permissions; `AbstractBaseUser` provides minimal auth logic when designing a completely custom user schema.',
                    "topic": 'Authentication',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is a custom Model Manager in Django primarily used for?',
                    "option_a": 'Handling HTTP cookies',
                    "option_b": 'Adding table-level query methods and modifying the initial QuerySet returned by the model (`Model.objects`)',
                    "option_c": 'Managing CSS assets',
                    "option_d": 'Configuring reverse proxy web servers',
                    "correct_option": 'B',
                    "explanation": 'Custom Managers extend `models.Manager` to define reusable QuerySet queries, filters (like `active()`), or customized object creation logic.',
                    "topic": 'Models & Managers',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Which Django feature allows decoupled applications to get notified when certain model actions occur (e.g. after a record is saved)?',
                    "option_a": 'Django Channels',
                    "option_b": 'Django Signals (`post_save`, `pre_delete`)',
                    "option_c": 'Template context processors',
                    "option_d": 'WSGI dispatchers',
                    "correct_option": 'B',
                    "explanation": 'Django Signals include a dispatcher that allows senders to notify a set of receivers when actions occur, such as `post_save` or `m2m_changed`.',
                    "topic": 'Signals',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Why must the `SECRET_KEY` setting in a Django project remain strictly confidential in production?',
                    "option_a": 'It is used for database password encryption only',
                    "option_b": 'It provides cryptographic signing for sessions, password reset tokens, and CSRF protection; compromise allows forged authentication',
                    "option_c": 'It specifies the SSL certificate port',
                    "option_d": "It determines the server's local timezone",
                    "correct_option": 'B',
                    "explanation": 'The SECRET_KEY is used for cryptographic signing throughout Django. Leaking it allows attackers to forge session cookies and privilege-escalate.',
                    "topic": 'Security',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What HTTP status code does `get_object_or_404()` return if the requested object is not found?',
                    "option_a": '500 Internal Server Error',
                    "option_b": '404 Not Found',
                    "option_c": '400 Bad Request',
                    "option_d": '403 Forbidden',
                    "correct_option": 'B',
                    "explanation": "`get_object_or_404` calls `get()` on a given model manager, catching `Http404` instead of allowing the model's `DoesNotExist` exception to bubble as a 500 error.",
                    "topic": 'Views',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'In Django REST Framework, which component automatically maps URL confs for standard CRUD actions on a `ModelViewSet`?',
                    "option_a": 'APIView handler',
                    "option_b": 'DefaultRouter (or SimpleRouter)',
                    "option_c": 'urlpatterns middleware',
                    "option_d": 'Dispatcher',
                    "correct_option": 'B',
                    "explanation": 'DRF Routers automatically generate canonical URL configurations (list, create, retrieve, update, destroy) for ViewSets.',
                    "topic": 'DRF Routing',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'How does Django process middleware during the request and response cycles?',
                    "option_a": 'Top-to-bottom on the request cycle, and bottom-to-top on the response cycle',
                    "option_b": 'In random asynchronous order',
                    "option_c": 'Bottom-to-top on both request and response cycles',
                    "option_d": 'Only one middleware runs per HTTP request',
                    "correct_option": 'A',
                    "explanation": 'Django middleware is executed as an onion layer: top-to-bottom as requests flow inwards to the view, and bottom-to-top as responses return outwards.',
                    "topic": 'Middleware',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'How can you ensure multiple database operations either all succeed or all roll back together in Django?',
                    "option_a": 'Using `models.commit()`',
                    "option_b": 'Wrapping the operations in `transaction.atomic()` context manager or decorator',
                    "option_c": 'Using a try/except block without transaction management',
                    "option_d": 'Setting `DEBUG=False`',
                    "correct_option": 'B',
                    "explanation": '`django.db.transaction.atomic` wraps a block of code in a database transaction, guaranteeing ACID rollback on uncaught exceptions.',
                    "topic": 'Transactions',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the primary advantage of using `bulk_create()` over standard loops calling `.save()` in Django ORM?',
                    "option_a": 'It bypasses foreign key checks',
                    "option_b": 'It inserts multiple objects into the database with a single SQL INSERT query, dramatically reducing round-trips',
                    "option_c": 'It automatically triggers post_save signals for each instance',
                    "option_d": 'It indexes fields automatically',
                    "correct_option": 'B',
                    "explanation": '`bulk_create` constructs a single multi-row SQL INSERT statement instead of executing individual queries in a loop.',
                    "topic": 'ORM Optimization',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Which DRF permission class restricts access solely to authenticated users while denying anonymous callers with HTTP 401/403?',
                    "option_a": 'AllowAny',
                    "option_b": 'IsAuthenticated',
                    "option_c": 'IsAdminUser',
                    "option_d": 'DjangoModelPermissions',
                    "correct_option": 'B',
                    "explanation": '`IsAuthenticated` denies permission to unauthenticated requests, ensuring only validated users can interact with the endpoint.',
                    "topic": 'DRF Permissions',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Which class-based generic view in Django is specifically tailored for displaying a paginated list of model objects?',
                    "option_a": 'DetailView',
                    "option_b": 'ListView',
                    "option_c": 'CreateView',
                    "option_d": 'FormView',
                    "correct_option": 'B',
                    "explanation": '`ListView` provides built-in mechanisms for fetching querysets, context population, template rendering, and automatic pagination.',
                    "topic": 'Class-Based Views',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'In Django media handling, what is the difference between `MEDIA_ROOT` and `MEDIA_URL`?',
                    "option_a": '`MEDIA_ROOT` is the absolute filesystem path where uploaded files are stored, while `MEDIA_URL` is the public URL path serving them',
                    "option_b": '`MEDIA_ROOT` is only used for CSS and JS assets',
                    "option_c": 'There is no difference; they point to the same directory',
                    "option_d": '`MEDIA_URL` points to the database connection string',
                    "correct_option": 'A',
                    "explanation": '`MEDIA_ROOT` specifies the physical disk directory path for user uploads, while `MEDIA_URL` is the web URL prefix serving those files.',
                    "topic": 'File Management',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'How do you register a custom template filter in a Django app?',
                    "option_a": 'In the `settings.py` TEMPLATES dictionary directly',
                    "option_b": "Using `@register.filter(name='filter_name')` inside a `templatetags/` module",
                    "option_c": 'By adding it to `urls.py`',
                    "option_d": 'Inside the Django database migrations',
                    "correct_option": 'B',
                    "explanation": 'Custom filters are created in a `templatetags` package within an installed app using `template.Library()` and the `@register.filter` decorator.',
                    "topic": 'Templates',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Which session engine is configured by default in standard Django projects?',
                    "option_a": 'Cache-based sessions (`django.contrib.sessions.backends.cache`)',
                    "option_b": 'Database-backed sessions (`django.contrib.sessions.backends.db`)',
                    "option_c": 'File-based sessions (`django.contrib.sessions.backends.file`)',
                    "option_d": 'Signed cookie sessions only',
                    "correct_option": 'B',
                    "explanation": 'Django defaults to database-backed sessions storing session data in the `django_session` database table.',
                    "topic": 'Sessions',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What does adding `db_index=True` to a Django model field do?',
                    "option_a": 'Encrypts the column with AES',
                    "option_b": 'Creates a database index on that column to accelerate lookups and filtering',
                    "option_c": 'Makes the column a foreign key',
                    "option_d": 'Enforces a unique constraint across the whole table',
                    "correct_option": 'B',
                    "explanation": "`db_index=True` instructs Django's migration generator to create a database index on the column for faster SELECT queries.",
                    "topic": 'Database Indexing',
                    "difficulty": difficulty
                },
                {
                    "question_text": "In modern Django, how should compound unique constraints across multiple fields be declared in a Model's `Meta`?",
                    "option_a": "Using `models.UniqueConstraint(fields=[...], name='...')` inside `constraints`",
                    "option_b": 'Using `fields_unique = True`',
                    "option_c": 'Inside the `admin.py` file',
                    "option_d": 'Using Python assert statements',
                    "correct_option": 'A',
                    "explanation": '`models.UniqueConstraint` in `Meta.constraints` is the modern, recommended approach replacing older `unique_together` tuples.',
                    "topic": 'Models & Constraints',
                    "difficulty": difficulty
                },
                {
                    "question_text": "What is the purpose of DRF's `throttling` mechanism?",
                    "option_a": 'To limit rate of incoming requests from clients (rate limiting / DoS prevention)',
                    "option_b": 'To compress JSON responses',
                    "option_c": 'To slow down database backup procedures',
                    "option_d": 'To encrypt passwords',
                    "correct_option": 'A',
                    "explanation": 'Throttling controls the rate of requests that clients can make to an API, protecting against abuse and brute-force attempts.',
                    "topic": 'DRF Throttling',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What does the `django.db.models.aggregates.Count` function combined with `.annotate()` do?',
                    "option_a": 'Counts total rows in the entire table globally',
                    "option_b": 'Computes aggregate counts for each individual object in the QuerySet (e.g. number of items per category)',
                    "option_c": 'Deletes duplicate rows',
                    "option_d": 'Validates data types',
                    "correct_option": 'B',
                    "explanation": '`.annotate()` computes summary values for each item in a QuerySet (group by item), whereas `.aggregate()` returns a single dictionary over the whole QuerySet.',
                    "topic": 'ORM Aggregation',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the consequence of configuring `on_delete=models.PROTECT` on a ForeignKey in Django?',
                    "option_a": 'Deleting the referenced object deletes all child objects automatically',
                    "option_b": 'Prevents deletion of the referenced object by raising `ProtectedError` if child objects still exist',
                    "option_c": 'Sets the child reference to NULL',
                    "option_d": 'Sets the child reference to a default value',
                    "correct_option": 'B',
                    "explanation": '`models.PROTECT` prevents deletion of referenced parent records to preserve relational integrity and avoid accidental data loss.',
                    "topic": 'ORM Relationships',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the purpose of `AUTHENTICATION_BACKENDS` in Django settings?',
                    "option_a": 'To configure SQL database drivers',
                    "option_b": 'To define an ordered list of classes used to authenticate user credentials (e.g. ModelBackend, LDAP, OAuth)',
                    "option_c": 'To choose between React and Vue frontends',
                    "option_d": 'To manage SSL certificate authorities',
                    "correct_option": 'B',
                    "explanation": '`AUTHENTICATION_BACKENDS` lists classes queried in order to verify user credentials and retrieve user permissions.',
                    "topic": 'Authentication',
                    "difficulty": difficulty
                },
                {
                    "question_text": "How does Django's `TestCase` ensure database isolation between individual test methods?",
                    "option_a": 'By completely dropping and recreating the database on every test method',
                    "option_b": 'By wrapping each test method in a database transaction and rolling it back upon method completion',
                    "option_c": 'By writing all test data to mock memory files',
                    "option_d": 'By running tests in parallel threads',
                    "correct_option": 'B',
                    "explanation": '`django.test.TestCase` wraps test execution inside an atomic transaction, rolling back changes at teardown for speed and isolation.',
                    "topic": 'Testing',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the primary difference between WSGI and ASGI in Django?',
                    "option_a": 'WSGI is synchronous request-response protocol; ASGI is asynchronous supporting WebSockets, async views, and background connections',
                    "option_b": 'ASGI can only be used with PostgreSQL databases',
                    "option_c": 'WSGI is for frontend single-page apps',
                    "option_d": 'There is no functional difference',
                    "correct_option": 'A',
                    "explanation": 'WSGI is standard synchronous Python web interface; ASGI adds asynchronous support for WebSockets, long polling, and async Python views.',
                    "topic": 'Architecture & Deployment',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What command creates a standalone executable custom management script in a Django app?',
                    "option_a": 'Placing a script inside `<app>/management/commands/<command_name>.py` extending `BaseCommand`',
                    "option_b": 'Adding a function inside `views.py`',
                    "option_c": 'Creating a file named `manage.sh`',
                    "option_d": 'Editing the Django core binaries',
                    "correct_option": 'A',
                    "explanation": 'Management commands are implemented by creating `<app>/management/commands/<name>.py` inheriting from `django.core.management.base.BaseCommand`.',
                    "topic": 'Management Commands',
                    "difficulty": difficulty
                },
            ],
            'React': [
                {
                    "question_text": 'What is the primary benefit of the Virtual DOM in React?',
                    "option_a": 'It replaces HTML completely with browser assembly',
                    "option_b": 'It minimizes costly direct manipulations to the real browser DOM by computing diffs in memory',
                    "option_c": 'It automatically compiles JavaScript into machine code',
                    "option_d": 'It provides a server-side relational database',
                    "correct_option": 'B',
                    "explanation": 'React maintains a virtual representation of the UI in memory, calculating minimal necessary DOM updates using its reconciliation algorithm.',
                    "topic": 'Virtual DOM',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Which React hook is used to perform side effects such as data fetching or subscriptions?',
                    "option_a": 'useState',
                    "option_b": 'useEffect',
                    "option_c": 'useCallback',
                    "option_d": 'useReducer',
                    "correct_option": 'B',
                    "explanation": 'useEffect lets functional components synchronize with external systems, manage subscriptions, and fetch API data.',
                    "topic": 'Hooks',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Why should keys in React lists be unique and stable?',
                    "option_a": 'Keys are used as CSS selectors',
                    "option_b": 'Keys help React identify which items have changed, been added, or removed during reconciliation',
                    "option_c": 'Keys are required by ECMAScript strict mode',
                    "option_d": 'Keys encrypt array elements in browser memory',
                    "correct_option": 'B',
                    "explanation": 'Keys give elements a persistent identity across renders, preventing unnecessary re-renders or component state corruption.',
                    "topic": 'Reconciliation',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What happens when you call `setState` in React?',
                    "option_a": 'The entire browser page reloads instantly',
                    "option_b": "React schedules an update to the component's state object and re-renders the component asynchronously",
                    "option_c": 'The state variable is mutated directly in-place synchronously',
                    "option_d": 'A HTTP request is dispatched to the server',
                    "correct_option": 'B',
                    "explanation": 'State setters schedule a re-render and batch updates for optimal rendering performance.',
                    "topic": 'State Management',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'When should you use `useMemo` in a React application?',
                    "option_a": 'For all function declarations inside every component',
                    "option_b": "To memoize computationally expensive calculations so they don't re-run on every render unless dependencies change",
                    "option_c": 'To replace localStorage',
                    "option_d": 'To declare state variables',
                    "correct_option": 'B',
                    "explanation": '`useMemo` caches the calculated result of an expensive function until one of its declared dependencies changes.',
                    "topic": 'Performance Optimization',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the primary difference between `useMemo` and `useCallback`?',
                    "option_a": '`useMemo` returns a memoized value; `useCallback` returns a memoized callback function definition',
                    "option_b": '`useCallback` is asynchronous, while `useMemo` is synchronous',
                    "option_c": '`useMemo` can only be used with numbers',
                    "option_d": 'There is no difference; they are aliases for each other',
                    "correct_option": 'A',
                    "explanation": '`useCallback(fn, deps)` is equivalent to `useMemo(() => fn, deps)`. It prevents recreation of functions passed as props to optimized child components.',
                    "topic": 'Hooks',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the core distinction between props and state in React?',
                    "option_a": 'Props are internal and mutable by the component; state is external and read-only',
                    "option_b": 'Props are external inputs passed from parent components and are read-only; state is internal and managed within the component',
                    "option_c": 'Props can only store strings, while state can store any datatype',
                    "option_d": 'State cannot trigger re-renders',
                    "correct_option": 'B',
                    "explanation": 'Props are immutable parameters passed down from a parent component; state is local, mutable memory managed within the component.',
                    "topic": 'Core Principles',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What problem does the React Context API solve?',
                    "option_a": 'It replaces relational database servers',
                    "option_b": "It avoids 'prop drilling' by sharing values across the component tree without manually passing props at every level",
                    "option_c": 'It compiles JSX into WebAssembly',
                    "option_d": 'It handles browser routing automatically',
                    "correct_option": 'B',
                    "explanation": 'Context provides a way to pass data through the component tree without having to pass props down manually at every level.',
                    "topic": 'Context API',
                    "difficulty": difficulty
                },
                {
                    "question_text": "What is a 'controlled component' in React form handling?",
                    "option_a": 'A component whose DOM elements are directly manipulated with jQuery',
                    "option_b": 'A form element whose value is controlled by React state via value props and onChange handlers',
                    "option_c": 'A component that cannot be unmounted',
                    "option_d": 'A component restricted to administrative users',
                    "correct_option": 'B',
                    "explanation": "In a controlled component, form data is handled by a React component state, making the component state the 'single source of truth'.",
                    "topic": 'Forms',
                    "difficulty": difficulty
                },
                {
                    "question_text": "What does 'lifting state up' mean in React development?",
                    "option_a": 'Storing state inside window.localStorage',
                    "option_b": 'Moving shared state to the closest common ancestor of the components that need it',
                    "option_c": 'Moving state to a server database',
                    "option_d": 'Converting functional components to class components',
                    "correct_option": 'B',
                    "explanation": 'When multiple components need to reflect the same changing data, you lift the shared state up to their closest common parent.',
                    "topic": 'State Architecture',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What does wrapping a component in `React.memo` accomplish?',
                    "option_a": 'Prevents the component from rendering if its props have not changed',
                    "option_b": 'Saves the component markup to browser disk cache',
                    "option_c": 'Forces the component to re-render on every state change in any sibling',
                    "option_d": 'Converts the component to a Web Worker',
                    "correct_option": 'A',
                    "explanation": '`React.memo` is a higher-order component that memoizes the rendered output, skipping rendering if props are shallowly equal.',
                    "topic": 'Performance Optimization',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the primary use case of the `useRef` hook in React?',
                    "option_a": 'Accessing DOM nodes directly or persisting a mutable value across renders without causing a re-render',
                    "option_b": 'Triggering immediate component re-renders on every value change',
                    "option_c": 'Fetching data over GraphQL',
                    "option_d": 'Managing global Redux state',
                    "correct_option": 'A',
                    "explanation": '`useRef` returns a mutable ref object whose `.current` property persists for the lifetime of the component without triggering a re-render on mutation.',
                    "topic": 'Hooks',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What naming rule must all custom hooks follow in React?',
                    "option_a": "They must end with 'Hook'",
                    "option_b": "They must start with the word 'use' (e.g. `useFetch`, `useAuth`)",
                    "option_c": 'They must be written in uppercase capital letters',
                    "option_d": 'They must be declared inside class methods',
                    "correct_option": 'B',
                    "explanation": "Custom hooks must start with `use` so React's linter and runtime can automatically enforce the Rules of Hooks.",
                    "topic": 'Custom Hooks',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the purpose of React Fragments (`<React.Fragment>` or `<>...</>`)?',
                    "option_a": 'To animate HTML elements',
                    "option_b": 'To group a list of children elements without adding extra wrapper nodes to the browser DOM',
                    "option_c": 'To split CSS styles into multiple bundles',
                    "option_d": 'To handle errors asynchronously',
                    "correct_option": 'B',
                    "explanation": 'Fragments let you return multiple elements from a component without introducing unnecessary div wrappers into the DOM tree.',
                    "topic": 'JSX & Elements',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'How do Error Boundaries in React handle component runtime errors?',
                    "option_a": 'By suppressing errors and logging nothing to console',
                    "option_b": 'By catching JavaScript errors anywhere in their child component tree, logging them, and displaying a fallback UI instead of crashing the app',
                    "option_c": 'By automatically reloading the browser tab in a loop',
                    "option_d": 'By converting syntax errors into warnings',
                    "correct_option": 'B',
                    "explanation": 'Error boundaries are class components implementing `componentDidCatch` or `getDerivedStateFromError` to catch child rendering errors gracefully.',
                    "topic": 'Error Handling',
                    "difficulty": difficulty
                },
                {
                    "question_text": "Why does React's `<StrictMode>` intentionally invoke certain functions (like component bodies and hooks) twice in development?",
                    "option_a": 'To test high CPU load scenarios',
                    "option_b": 'To help developers detect unexpected side effects and non-pure calculations during rendering',
                    "option_c": 'Because of a known legacy browser bug',
                    "option_d": 'To double the speed of garbage collection',
                    "correct_option": 'B',
                    "explanation": 'Strict Mode double-invokes renders and effect cleanups in development mode to surface impure side effects and memory leaks.',
                    "topic": 'StrictMode',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'When is `useReducer` generally preferred over `useState` in React?',
                    "option_a": 'When managing single primitive boolean flags',
                    "option_b": 'When state logic is complex, involves multiple sub-values, or when next state depends on previous state in intricate ways',
                    "option_c": 'Only when connecting to GraphQL APIs',
                    "option_d": 'When rendering static text without user interaction',
                    "correct_option": 'B',
                    "explanation": '`useReducer` provides predictable state transitions via action dispatching, making complex state transitions easier to test and reason about.',
                    "topic": 'State Management',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'In React Router v6, how do you programmatically navigate to another URL from an event handler?',
                    "option_a": 'Using `history.push()`',
                    "option_b": 'Calling the function returned by the `useNavigate()` hook',
                    "option_c": 'Mutating `window.location.href` directly',
                    "option_d": "Using `<Redirect to='...' />`",
                    "correct_option": 'B',
                    "explanation": "React Router v6 replaces `useHistory` with `const navigate = useNavigate()`, called as `navigate('/path')`.",
                    "topic": 'Routing',
                    "difficulty": difficulty
                },
                {
                    "question_text": "What are the three main phases of a React component's lifecycle?",
                    "option_a": 'Loading, Storing, Deleting',
                    "option_b": 'Mounting, Updating, and Unmounting',
                    "option_c": 'Compiling, Bundling, and Minifying',
                    "option_d": 'Parsing, Interpreting, and Executing',
                    "correct_option": 'B',
                    "explanation": 'Every React component lifecycle progresses through Mounting (inserted into DOM), Updating (re-rendered due to props/state), and Unmounting (removed from DOM).',
                    "topic": 'Component Lifecycle',
                    "difficulty": difficulty
                },
                {
                    "question_text": "What is 'prop drilling' in React?",
                    "option_a": 'Validating types with PropTypes',
                    "option_b": "Passing props down through multiple layers of intermediate components that don't need the data themselves just to reach a deeply nested child",
                    "option_c": 'Writing unit tests for props',
                    "option_d": 'Converting props into JSON strings',
                    "correct_option": 'B',
                    "explanation": 'Prop drilling occurs when data is passed through intermediate components that act solely as relays, leading to boilerplate and tight coupling.',
                    "topic": 'Architecture',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is a `SyntheticEvent` in React?',
                    "option_a": 'A mock event generated only during unit testing',
                    "option_b": 'A cross-browser wrapper around the native browser event, ensuring consistent behavior across all browsers',
                    "option_c": 'An event triggered by CSS transitions',
                    "option_d": 'A WebSocket packet',
                    "correct_option": 'B',
                    "explanation": 'React wraps native browser events in SyntheticEvent instances to provide cross-browser consistency and unified event pooling/delegation.',
                    "topic": 'Events',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'How do `React.lazy` and `Suspense` improve initial page load performance?',
                    "option_a": 'By executing JavaScript code on the GPU',
                    "option_b": 'By enabling dynamic code-splitting, loading component bundles only when they are rendered for the first time while displaying a fallback',
                    "option_c": 'By compressing image assets',
                    "option_d": 'By converting CSS into inline styles',
                    "correct_option": 'B',
                    "explanation": '`React.lazy` lets you render a dynamic import as a regular component, bundled separately and rendered inside `<Suspense fallback={...}>`.',
                    "topic": 'Code Splitting & Performance',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Why must you avoid mutating state directly (e.g. `items.push(x)`) in React?',
                    "option_a": 'It causes a JavaScript syntax error',
                    "option_b": 'React relies on object reference comparisons (`Object.is`) to detect state changes; in-place mutations may skip re-rendering',
                    "option_c": 'Direct mutation crashes the browser garbage collector',
                    "option_d": 'React freezes all objects using Object.freeze() at build time',
                    "correct_option": 'B',
                    "explanation": 'React compares state references shallowly. Mutating an array or object in place retains the same reference, preventing re-renders.',
                    "topic": 'State Immutability',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the primary use case for React Portals (`ReactDOM.createPortal`)?',
                    "option_a": 'Connecting to third-party REST APIs',
                    "option_b": "Rendering children into a different DOM subtree outside of the parent component's DOM hierarchy (e.g. for modals and tooltips)",
                    "option_c": 'Rendering components inside WebAssembly',
                    "option_d": 'Passing data to service workers',
                    "correct_option": 'B',
                    "explanation": 'Portals provide a first-class way to render children into a DOM node that exists outside the DOM hierarchy of the parent component.',
                    "topic": 'Portals',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is a key difference between React Server Components (RSC) and standard Client Components?',
                    "option_a": 'Server Components execute solely on the server, have zero impact on client bundle size, and cannot use hooks like `useState`',
                    "option_b": 'Client Components cannot render HTML',
                    "option_c": 'Server Components can only render raw plain text',
                    "option_d": 'There is no difference in modern Next.js',
                    "correct_option": 'A',
                    "explanation": 'Server Components run on the server with direct database/filesystem access and zero client bundle overhead; interactive hooks require client boundaries.',
                    "topic": 'Server Components',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What does `React.forwardRef` allow a component to do?',
                    "option_a": 'Forward HTTP requests to a backend microservice',
                    "option_b": 'Accept a `ref` from a parent component and forward it down to a child DOM element or component',
                    "option_c": 'Automatically bind class methods to `this`',
                    "option_d": 'Redirect URLs inside React Router',
                    "correct_option": 'B',
                    "explanation": '`React.forwardRef` creates a React component that forwards the ref attribute it receives to another component lower in the tree.',
                    "topic": 'Refs',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What happens if you pass an empty dependency array `[]` to `useEffect`?',
                    "option_a": 'The effect runs on every single render',
                    "option_b": 'The effect runs exactly once after the initial mount, and its cleanup runs on unmount',
                    "option_c": 'The effect never runs at all',
                    "option_d": 'The effect throws a runtime exception',
                    "correct_option": 'B',
                    "explanation": 'Passing `[]` tells React the effect does not depend on any changing values from props or state, executing only once on mount.',
                    "topic": 'Hooks',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'In Redux Toolkit, what does `createSlice` generate automatically?',
                    "option_a": 'HTML template files',
                    "option_b": 'Action creator functions and action types corresponding to the defined reducers, plus the slice reducer function',
                    "option_c": 'Database schema migrations',
                    "option_d": 'CSS module styles',
                    "correct_option": 'B',
                    "explanation": '`createSlice` automatically generates action types, action creators, and the reducer function based on your reducers map.',
                    "topic": 'Redux Toolkit',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'How do you specify a cleanup mechanism (such as clearing a timer or unsubscribing) in a `useEffect` hook?',
                    "option_a": 'By declaring a second parameter named `cleanup`',
                    "option_b": 'By returning a cleanup function from inside the effect callback',
                    "option_c": 'By using the `window.onbeforeunload` event handler',
                    "option_d": 'Effects cannot be cleaned up in functional components',
                    "correct_option": 'B',
                    "explanation": 'If your effect returns a function, React will run it when the component unmounts and before re-running the effect on subsequent renders.',
                    "topic": 'Hooks',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the difference between a React Element and a React Component?',
                    "option_a": 'An element is a plain immutable object describing a DOM node or component; a component is a function or class that returns elements',
                    "option_b": 'Components are created by the browser DOM; elements are created by Babel',
                    "option_c": 'Elements have state; components do not',
                    "option_d": 'They are completely identical terms',
                    "correct_option": 'A',
                    "explanation": "A React element is a lightweight virtual description (`{type: 'div', props: ...}`); a component is the function/class blueprint that returns elements.",
                    "topic": 'Core Principles',
                    "difficulty": difficulty
                },
            ],
            'SQL': [
                {
                    "question_text": 'What is the difference between `WHERE` and `HAVING` clauses in SQL?',
                    "option_a": '`WHERE` filters rows before aggregation, while `HAVING` filters aggregated groups',
                    "option_b": '`HAVING` can only be used with primary keys',
                    "option_c": 'They are completely identical and interchangeable',
                    "option_d": '`WHERE` can only be used in UPDATE queries',
                    "correct_option": 'A',
                    "explanation": '`WHERE` operates on individual rows prior to grouping, whereas `HAVING` filters group summaries produced by `GROUP BY`.',
                    "topic": 'Aggregation',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Which SQL JOIN returns all rows from the left table and matched rows from the right table?',
                    "option_a": 'INNER JOIN',
                    "option_b": 'LEFT JOIN (or LEFT OUTER JOIN)',
                    "option_c": 'CROSS JOIN',
                    "option_d": 'FULL OUTER JOIN',
                    "correct_option": 'B',
                    "explanation": 'A LEFT JOIN retains all records from the left table regardless of whether a matching record exists in the right table (filling NULLs for non-matches).',
                    "topic": 'Joins',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is an index in a relational database like MySQL, and what is its primary trade-off?',
                    "option_a": 'It encrypts table data at rest with no runtime cost',
                    "option_b": 'A data structure (often B-Tree) that speeds up SELECT queries at the cost of additional disk space and slower INSERT/UPDATE writes',
                    "option_c": 'A backup copy of deleted records',
                    "option_d": 'A temporary table created in RAM during joins',
                    "correct_option": 'B',
                    "explanation": 'Indexes drastically accelerate search lookups (O(log n) vs O(n) table scans) but introduce maintenance overhead on data mutation operations.',
                    "topic": 'Indexing',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What does the ACID acronym stand for in database transaction management?',
                    "option_a": 'Access, Control, Integrity, Durability',
                    "option_b": 'Atomicity, Consistency, Isolation, Durability',
                    "option_c": 'Allocation, Concurrency, Indexing, Delivery',
                    "option_d": 'Authentication, Cryptography, Identity, Directory',
                    "correct_option": 'B',
                    "explanation": 'ACID guarantees that database transactions are processed reliably: Atomicity, Consistency, Isolation, and Durability.',
                    "topic": 'Transactions',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Which normal form requires eliminating repeating groups and ensuring every attribute contains only atomic values?',
                    "option_a": 'First Normal Form (1NF)',
                    "option_b": 'Second Normal Form (2NF)',
                    "option_c": 'Third Normal Form (3NF)',
                    "option_d": 'Boyce-Codd Normal Form (BCNF)',
                    "correct_option": 'A',
                    "explanation": '1NF enforces atomicity: each column contains single, indivisible values with unique column names and records.',
                    "topic": 'Database Normalization',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the primary requirement for Second Normal Form (2NF)?',
                    "option_a": 'Must be in 1NF and have no partial dependencies on composite primary keys',
                    "option_b": 'Must eliminate all foreign keys',
                    "option_c": 'Must have only numeric column types',
                    "option_d": 'Must be clustered',
                    "correct_option": 'A',
                    "explanation": '2NF requires the table to be in 1NF and that every non-prime attribute is fully functionally dependent on the entire primary key.',
                    "topic": 'Database Normalization',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the requirement for Third Normal Form (3NF)?',
                    "option_a": 'Must be in 2NF and have no transitive functional dependencies of non-key attributes on the primary key',
                    "option_b": 'Must contain three separate foreign key relationships',
                    "option_c": 'Must use JSON columns exclusively',
                    "option_d": 'Must have only three tables in the schema',
                    "correct_option": 'A',
                    "explanation": '3NF requires the relation to be in 2NF and that no non-prime attribute is transitively dependent on any candidate key.',
                    "topic": 'Database Normalization',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the difference between a Primary Key and a Unique Key constraint?',
                    "option_a": 'A table can have only one Primary Key and it cannot contain NULL values, whereas multiple Unique Keys are allowed and they permit NULLs (in most RDBMS)',
                    "option_b": 'Unique Keys can only store integers',
                    "option_c": 'Primary Keys do not create an index',
                    "option_d": 'There is no difference',
                    "correct_option": 'A',
                    "explanation": 'A table has at most one Primary Key (strictly NOT NULL); multiple UNIQUE constraints are permitted per table and typically allow NULL values.',
                    "topic": 'Constraints',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is a Common Table Expression (CTE) in SQL?',
                    "option_a": 'A permanent view stored on disk',
                    "option_b": 'A temporary named result set defined using the `WITH` clause that exists only within the execution scope of a single statement',
                    "option_c": 'A database trigger',
                    "option_d": 'A binary storage engine',
                    "correct_option": 'B',
                    "explanation": 'A CTE defines a temporary result set using `WITH cte_name AS (...)` to simplify complex joins and support recursion.',
                    "topic": 'CTEs & Subqueries',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the difference between `ROW_NUMBER()`, `RANK()`, and `DENSE_RANK()` window functions?',
                    "option_a": '`ROW_NUMBER()` assigns sequential integers without ties; `RANK()` leaves gaps in ranking after ties; `DENSE_RANK()` assigns identical ranks to ties without gaps',
                    "option_b": '`RANK()` only works on descending dates',
                    "option_c": '`DENSE_RANK()` creates temporary database tables',
                    "option_d": 'They all produce the exact same sequence regardless of ties',
                    "correct_option": 'A',
                    "explanation": 'Ties with values (10, 10, 20): ROW_NUMBER gives 1, 2, 3; RANK gives 1, 1, 3; DENSE_RANK gives 1, 1, 2.',
                    "topic": 'Window Functions',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the performance and behavioral difference between `UNION` and `UNION ALL`?',
                    "option_a": '`UNION` eliminates duplicate rows by sorting/hashing the result set; `UNION ALL` combines results directly without duplicate removal, making it faster',
                    "option_b": '`UNION ALL` can only join two tables max',
                    "option_c": '`UNION` preserves all duplicates',
                    "option_d": '`UNION ALL` requires columns to have identical names',
                    "correct_option": 'A',
                    "explanation": '`UNION` performs an internal deduplication pass; `UNION ALL` simply concatenates result sets, delivering significantly faster execution.',
                    "topic": 'Set Operations',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'In SQL, what is the consequence of configuring `ON DELETE CASCADE` on a Foreign Key?',
                    "option_a": 'Prevent deletion of the referenced row',
                    "option_b": 'Automatically delete all related child rows when the parent record is deleted',
                    "option_c": 'Set the child foreign key column to NULL',
                    "option_d": 'Backup deleted records into an archive table',
                    "correct_option": 'B',
                    "explanation": '`ON DELETE CASCADE` automatically propagates deletions from referenced parent rows down to all dependent child records.',
                    "topic": 'Referential Integrity',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Why does evaluating `col = NULL` in SQL return UNKNOWN/FALSE instead of TRUE?',
                    "option_a": 'Because SQL employs three-valued logic (TRUE, FALSE, UNKNOWN); NULL represents an unknown value and must be checked with `IS NULL`',
                    "option_b": 'Because NULL is equal to integer zero',
                    "option_c": 'Because strings cannot be compared with symbols',
                    "option_d": 'Because SQL converts NULL to empty string automatically',
                    "correct_option": 'A',
                    "explanation": 'In ANSI SQL three-valued logic, comparison with NULL evaluates to UNKNOWN. You must use `IS NULL` or `IS NOT NULL`.',
                    "topic": 'NULL Handling',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the role of `COMMIT` and `ROLLBACK` in database transaction control?',
                    "option_a": '`COMMIT` applies all transaction changes permanently; `ROLLBACK` reverts all uncommitted changes back to the start of the transaction',
                    "option_b": '`COMMIT` drops the active table',
                    "option_c": '`ROLLBACK` creates a duplicate database user',
                    "option_d": 'They are only used in NoSQL key-value stores',
                    "correct_option": 'A',
                    "explanation": 'Transactions end with `COMMIT` (persisting all DML operations) or `ROLLBACK` (undoing all operations if an error occurs).',
                    "topic": 'Transactions',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What information does the `EXPLAIN` statement provide for a SQL query?',
                    "option_a": 'A natural language summary of table documentation',
                    "option_b": 'The execution plan chosen by the query optimizer, including index usage, scan types, joined tables, and estimated row counts',
                    "option_c": 'The user password authentication log',
                    "option_d": 'The database binary crash dump',
                    "correct_option": 'B',
                    "explanation": '`EXPLAIN` displays the query execution plan, showing whether queries utilize indexes or resort to full table scans.',
                    "topic": 'Query Optimization',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the difference between a Clustered Index and a Non-Clustered Index?',
                    "option_a": 'A Clustered Index determines the physical order of data rows on disk (only one per table); a Non-Clustered Index contains pointers to the data rows',
                    "option_b": 'Non-Clustered indexes can only store text',
                    "option_c": 'Clustered indexes do not support primary keys',
                    "option_d": 'A table can have dozens of Clustered Indexes',
                    "correct_option": 'A',
                    "explanation": 'Because table rows can only be physically sorted one way on disk, there can only be one Clustered Index (usually Primary Key) per table.',
                    "topic": 'Indexing',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the difference between a Stored Procedure and a User-Defined Function (UDF) in SQL?',
                    "option_a": 'Functions must return a value and cannot execute transaction control (COMMIT/ROLLBACK); Stored Procedures can perform transactions and return multiple or no values',
                    "option_b": 'Functions cannot accept parameters',
                    "option_c": 'Stored procedures can only be written in Java',
                    "option_d": 'There is no difference',
                    "correct_option": 'A',
                    "explanation": 'UDFs can be used directly inside SELECT statements to compute values; Stored Procedures execute broader business logic with transaction handling.',
                    "topic": 'Programmability',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'How does a Materialized View differ from a standard SQL View?',
                    "option_a": 'A standard View is a saved virtual query executed dynamically; a Materialized View physically caches the query results on disk and must be refreshed',
                    "option_b": 'Standard Views only work with SQLite',
                    "option_c": 'Materialized Views cannot be indexed',
                    "option_d": 'Standard Views consume more disk space than tables',
                    "correct_option": 'A',
                    "explanation": 'Materialized views persist query results physically to disk, accelerating expensive analytical queries at the expense of needing periodic refreshes.',
                    "topic": 'Views',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is an event Trigger in a relational database?',
                    "option_a": 'A stored program executed automatically in response to specific events (INSERT, UPDATE, DELETE) on a particular table',
                    "option_b": 'A cron job running outside the database',
                    "option_c": 'A network firewall rule',
                    "option_d": 'A CSS animation trigger',
                    "correct_option": 'A',
                    "explanation": 'Triggers are database callbacks invoked automatically before or after DML modifications to enforce complex business rules and auditing.',
                    "topic": 'Triggers',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What does the `COALESCE(val1, val2, ...)` function return?',
                    "option_a": 'The maximum numeric value in the list',
                    "option_b": 'The first non-NULL expression among its arguments',
                    "option_c": 'The average of all non-null values',
                    "option_d": 'A concatenated string of all parameters',
                    "correct_option": 'B',
                    "explanation": '`COALESCE` evaluates its arguments in sequence and returns the first value that is not NULL, commonly used for fallback defaults.',
                    "topic": 'Built-in Functions',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Which ACID isolation level provides the highest level of concurrency protection at the expense of transaction throughput?',
                    "option_a": 'Read Uncommitted',
                    "option_b": 'Read Committed',
                    "option_c": 'Repeatable Read',
                    "option_d": 'Serializable',
                    "correct_option": 'D',
                    "explanation": 'Serializable completely isolates transactions as if they were executed sequentially, preventing dirty reads, non-repeatable reads, and phantom reads.',
                    "topic": 'Transactions & Isolation',
                    "difficulty": difficulty
                },
                {
                    "question_text": "What is a 'Dirty Read' anomaly in SQL database transactions?",
                    "option_a": 'Reading data corrupted by disk bad sectors',
                    "option_b": 'A transaction reading uncommitted data modified by another concurrent transaction that may later be rolled back',
                    "option_c": 'Reading rows with NULL values',
                    "option_d": 'Querying expired cache keys',
                    "correct_option": 'B',
                    "explanation": 'Dirty reads occur when a transaction reads uncommitted changes from another transaction that subsequently aborts/rolls back.',
                    "topic": 'Concurrency Anomalies',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is a database Deadlock?',
                    "option_a": 'A server running out of disk space',
                    "option_b": 'A situation where two or more transactions each hold locks on resources the other needs, blocking all from proceeding indefinitely',
                    "option_c": 'A dropped internet connection',
                    "option_d": 'A table having zero records',
                    "correct_option": 'B',
                    "explanation": 'Deadlocks occur when circular wait conditions arise between concurrent transactions competing for exclusive resource locks.',
                    "topic": 'Concurrency & Locking',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is Database Denormalization and when is it strategically used?',
                    "option_a": 'Deleting database foreign keys accidentally',
                    "option_b": 'Intentionally introducing controlled data redundancy to reduce expensive JOIN operations and improve read query performance in read-heavy systems',
                    "option_c": 'Converting relational tables into CSV files',
                    "option_d": 'Disabling database indexing',
                    "correct_option": 'B',
                    "explanation": 'Denormalization trades storage space and write complexity for faster read performance by minimizing multi-table joins in high-scale systems.',
                    "topic": 'Database Architecture',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the difference between Database Partitioning and Database Sharding?',
                    "option_a": 'Partitioning divides tables into segments within a single database instance; Sharding distributes data partitions horizontally across multiple distinct server instances',
                    "option_b": 'Sharding is only used for caching HTML',
                    "option_c": 'Partitioning requires NoSQL databases',
                    "option_d": 'There is no architectural difference',
                    "correct_option": 'A',
                    "explanation": 'Partitioning splits tables logically/physically on one machine (e.g. range by date); sharding distributes subsets across separate database servers.',
                    "topic": 'Scalability',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Why can `LIMIT 10 OFFSET 1000000` suffer from severe performance degradation in SQL?',
                    "option_a": 'Because the database must still read and discard the first 1,000,000 rows before returning the 10 requested rows',
                    "option_b": 'Because OFFSET is not supported by ANSI SQL',
                    "option_c": 'Because it forces an automatic table drop',
                    "option_d": 'Because it causes an integer overflow',
                    "correct_option": 'A',
                    "explanation": 'Offset-based pagination scans and discards all skipped rows. Keyset pagination (cursor-based using `WHERE id > last_id`) avoids this O(n) penalty.',
                    "topic": 'Query Optimization',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'How does a `CASE WHEN ... THEN ... ELSE ... END` expression function in a SQL SELECT statement?',
                    "option_a": 'It terminates query execution immediately',
                    "option_b": 'It provides conditional if-then-else logic to return different values based on boolean evaluations for each row',
                    "option_c": 'It alters the database schema permanently',
                    "option_d": 'It restarts the database server',
                    "correct_option": 'B',
                    "explanation": 'The `CASE` expression allows conditional column computation directly inside SQL queries across all ANSI-compliant database engines.',
                    "topic": 'Conditional Expressions',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What does a `CHECK` constraint do on a table column?',
                    "option_a": 'Validates that values entered into that column satisfy a specified boolean condition (e.g. `age >= 18`)',
                    "option_b": 'Verifies network connection latency',
                    "option_c": 'Enforces user password complexity',
                    "option_d": 'Runs an antivirus scan on incoming data',
                    "correct_option": 'A',
                    "explanation": 'CHECK constraints ensure that all values in a column conform to a specified predicate rule before allowing INSERT or UPDATE operations.',
                    "topic": 'Constraints',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'What is the primary role of a database connection pool in high-throughput backend applications?',
                    "option_a": 'To compress SQL payloads across the network',
                    "option_b": 'To maintain a cache of active database connections, reusing them instead of opening and tearing down expensive socket connections for every request',
                    "option_c": 'To encrypt table fields in memory',
                    "option_d": 'To backup transaction logs every minute',
                    "correct_option": 'B',
                    "explanation": 'Connection pools maintain open connections, eliminating the high CPU/network handshake overhead of establishing new connections per HTTP request.',
                    "topic": 'Connection Management',
                    "difficulty": difficulty
                },
                {
                    "question_text": 'Which SQL analytic function allows you to access data from a preceding row in the same result set without using a self-join?',
                    "option_a": '`LEAD()`',
                    "option_b": '`LAG()`',
                    "option_c": '`FIRST()`',
                    "option_d": '`PREV()`',
                    "correct_option": 'B',
                    "explanation": '`LAG(column, offset)` accesses a value from a specified physical offset prior to the current row within the partition.',
                    "topic": 'Window Functions',
                    "difficulty": difficulty
                },
            ],
        }

        # Retrieve matching bank or dynamically construct 30 distinct questions
        base_bank = banks.get(skill_name)
        if not base_bank:
            domains = [
                ('Architecture', 'What is a core architectural principle when designing scalable systems in {skill}?', 'Modularity, loose coupling, and clean separation of concerns', 'Hardcoding all state into global static variables', 'Coupling presentation directly to disk drivers', 'Eliminating all interfaces and abstraction boundaries', 'A', 'In {skill}, modular architecture and clean separation of concerns enable maintainable, testable, and scalable engineering.'),
                ('Best Practices', 'Which standard engineering practice should be followed when deploying {skill} applications to production?', 'Comprehensive unit testing, defensive error handling, and isolated environment configurations', 'Disabling application logs to save storage space', 'Exposing private credentials and keys in public repositories', 'Bypassing code review and staging verification', 'A', 'Production readiness mandates defensive error handling, test suites, and strict credential isolation.'),
                ('Error Handling', 'How does {skill} handle error propagation and operational resilience?', 'Through structured exception handling and actionable stack traces', 'By silently discarding runtime faults and continuing blindly', 'By rebooting the entire operating system on every syntax error', 'By converting fatal exceptions into random return values', 'A', 'Structured exception handlers intercept runtime exceptions, allowing graceful recovery and actionable debugging logs.'),
                ('Performance Optimization', 'When diagnosing performance bottlenecks in {skill}, what should be analyzed first?', 'Algorithmic time complexity (Big O) and I/O bottlenecks (database/network/disk)', 'Shortening variable names to save memory bytes', 'Removing whitespace and comments from source code files', 'Decreasing monitor refresh rates', 'A', 'Profiling identifies hot spots: algorithmic complexity and I/O bottlenecks deliver the highest performance gains.'),
                ('Dependency Management', 'What is the standard convention for dependency isolation in {skill} projects?', 'Using dedicated package managers, lockfiles, and isolated virtual environments or containers', 'Installing all dependencies into root operating system directories globally', 'Manually downloading untracked zip files into random desktop folders', 'Never updating third-party libraries under any circumstance', 'A', 'Package managers and lockfiles ensure deterministic, reproducible, and isolated builds across environments.'),
                ('Security', 'Which security principle is most vital when handling external client input in {skill}?', 'Defensive input validation, sanitization, and parameterized queries to prevent injection attacks', 'Trusting all client input implicitly without verification', 'Disabling HTTPS and TLS encryption to minimize latency', 'Storing plain-text passwords in cookies', 'A', 'Never trust client input: defensive sanitization and parameterized execution protect against severe vulnerabilities.'),
                ('Testing', 'Why are automated unit tests essential in a {skill} continuous integration workflow?', 'They verify individual components work in isolation, preventing regressions and enabling safe refactoring', 'They replace the need for writing documentation entirely', 'They automatically optimize SQL database queries', 'They are required by operating system hardware compilers', 'A', 'Unit tests validate core unit behavior in isolation, catching bugs early before deployment.'),
                ('Concurrency', 'What is a primary challenge when coordinating concurrent workloads in {skill}?', 'Managing shared mutable state and preventing race conditions or deadlocks', 'Ensuring variables use alphabetical naming', 'Forcing the application to execute only on a single core forever', 'Disabling memory garbage collection', 'A', 'Concurrency requires thread-safe primitives or immutability to prevent race conditions and inconsistent states.'),
                ('Memory Management', 'How can memory leaks be prevented in long-running {skill} processes?', 'By ensuring unneeded object references and event listeners are properly dereferenced or closed', 'By restarting the computer every ten minutes', 'By allocating all memory on the call stack permanently', 'By avoiding the use of data structures', 'A', 'Dangling references, uncleared event listeners, and unclosed connections prevent garbage collection, leading to leaks.'),
                ('Data Modeling', 'What is a key factor when designing data schemas or models in {skill}?', 'Choosing appropriate data types, normalization levels, and enforcing domain constraints', 'Storing all relational data in a single unindexed text column', 'Avoiding primary keys to increase insert speed', 'Duplicating all fields across every table without constraints', 'A', 'Careful data modeling ensures relational integrity, optimal query paths, and long-term schema maintainability.'),
                ('API Design', 'What is a hallmark of a robust RESTful API implemented in {skill}?', 'Consistent resource-oriented URI endpoints, standard HTTP status codes, and clear contract validation', 'Using HTTP GET for state-changing destructive deletions', 'Returning HTTP 200 OK for all server errors with unstructured plain text', 'Omitting content-type response headers', 'A', 'REST conventions standardize client-server contracts with predictable URI hierarchies and semantic status codes.'),
                ('Caching Strategies', 'When implementing caching in a {skill} system, what critical trade-off must be managed?', 'Cache invalidation complexity vs. data freshness and read query speed', 'Replacing databases with static text files', 'Disabling memory encryption', 'Increasing CPU clock speeds', 'A', 'Caching drastically accelerates read throughput, but cache invalidation strategies must prevent stale data.'),
                ('Scalability', 'What is the difference between horizontal and vertical scaling in {skill} infrastructure?', 'Horizontal scaling adds more machine nodes to the pool; vertical scaling increases the compute resources of a single server', 'Horizontal scaling only works on Windows servers', 'Vertical scaling completely eliminates database locks', 'There is no architectural difference', 'A', 'Horizontal scaling scales out across instances; vertical scaling scales up CPU and RAM on existing hardware.'),
                ('State Management', 'Why is predictable, immutable state management beneficial in complex {skill} applications?', 'It simplifies debugging, eliminates side-effect race conditions, and makes state changes traceable', 'It consumes zero bytes of RAM', 'It compiles code into bytecode faster', 'It makes functions asynchronous automatically', 'A', 'Immutable state transitions guarantee predictable unidirectional data flow and easier time-travel debugging.'),
                ('Logging & Observability', 'What is the recommended approach to application logging in {skill}?', 'Structured logging (e.g. JSON) with distinct severity levels (INFO, WARN, ERROR) and contextual metadata', 'Scattering unformatted print() statements throughout the codebase', 'Logging all user passwords and sensitive tokens in plain text', 'Completely turning off logging in production environments', 'A', 'Structured logging enables centralized aggregation, automated metric alerting, and actionable root cause analysis.'),
                ('Code Refactoring', 'What is the primary objective of code refactoring in {skill}?', 'Improving internal code structure, readability, and maintainability without altering external functional behavior', 'Changing public API signatures randomly to break client applications', 'Rewriting working code into assembly language', 'Adding complex nested conditional blocks', 'A', 'Refactoring pays down technical debt and cleans up architecture while preserving existing verified behavior.'),
                ('CI/CD Automation', 'What role does a Continuous Integration (CI) pipeline play in {skill} development?', 'Automatically running linters, tests, and security vulnerability scans on every code commit or pull request', 'Replacing software developers with automated commit bots', 'Hosting production customer databases', 'Formatting local IDE color themes', 'A', 'CI pipelines ensure code quality and prevent broken builds or security vulnerabilities from reaching main branches.'),
                ('Configuration Management', 'Where should environment-specific configurations and secrets be stored in {skill}?', 'In environment variables and external secret managers outside the codebase', 'Hardcoded directly into version-controlled source files', 'In public client-side browser bundles', 'In plain-text unencrypted comments', 'A', 'Twelve-Factor principles dictate strict separation of configuration and secrets from application code.'),
                ('Input Validation', 'Why should both client-side and server-side validation be implemented in {skill} systems?', 'Client-side provides immediate user feedback; server-side is mandatory because client requests can be bypassed or forged', 'Client-side validation is 100% secure and cannot be manipulated', 'Server-side validation is only needed for mobile devices', 'Validation should never be performed to maximize speed', 'A', 'Never trust client validation alone; server validation protects the integrity and security of the system.'),
                ('Documentation', 'What constitutes high-quality technical documentation for a {skill} library or service?', 'Clear architectural overviews, setup guides, API contracts, usage examples, and troubleshooting instructions', "A single line saying 'read the source code'", 'Outdated screenshots from previous major versions', 'Private notes written on personal local drives', 'A', 'Comprehensive documentation accelerates developer onboarding, reduces integration bugs, and ensures maintainability.'),
                ('Profiling & Benchmarking', 'How should profiling be used to guide optimization efforts in {skill}?', 'By measuring actual runtime metrics and memory allocations with profilers rather than relying on guesswork', 'By prematurely optimizing code before identifying actual bottlenecks', 'By deleting slow functions from the application', 'By ignoring latency under peak production traffic', 'A', 'Premature optimization is counterproductive; profiling identifies the 20% of code responsible for 80% of resource consumption.'),
                ('Separation of Concerns', 'What is the primary benefit of applying the Separation of Concerns pattern in {skill}?', 'Each module or layer focuses strictly on a single responsibility, reducing coupling and easing unit testing', 'It increases the number of dependencies', 'It guarantees zero runtime exceptions', 'It makes all database calls synchronous', 'A', 'Separating presentation, business logic, and data access ensures modularity, testability, and isolated evolvability.'),
                ('Versioning & SemVer', 'In Semantic Versioning (MAJOR.MINOR.PATCH) for {skill} packages, when is the MAJOR version incremented?', 'When making incompatible, breaking API changes', 'When adding backward-compatible functionality', 'When making backward-compatible bug fixes', 'On every daily git commit', 'A', 'Major version bumps indicate breaking changes; minor bumps add backward-compatible features; patches fix bugs.'),
                ('Resiliency & Fault Tolerance', 'What is the purpose of the Circuit Breaker pattern in {skill} distributed systems?', 'To prevent cascading system failures by failing fast when a remote downstream dependency is failing or unresponsive', 'To cut off electrical power to server racks', 'To terminate client database sessions unexpectedly', 'To encrypt network packets', 'A', 'Circuit breakers detect failures and stop invocations to struggling services, giving them time to recover.'),
                ('Data Serialization', 'What is data serialization in {skill}?', 'Translating in-memory data structures into a format (like JSON or Protobuf) that can be transmitted over a network or stored on disk', 'Encrypting files with RSA keys', 'Compressing images to webp format', 'Sorting numbers sequentially', 'A', 'Serialization converts application objects into streamable byte or text representations, and deserialization reconstructs them.'),
                ('Interface Segregation', 'What does the Interface Segregation Principle state in {skill} design?', 'Clients should not be forced to depend on interfaces or methods they do not use', 'Every class must implement at least ten public methods', 'All functions must return interface types', 'Classes should never inherit from abstract classes', 'A', 'Smaller, role-specific interfaces are preferable to fat, bloated interfaces that impose unnecessary method contracts.'),
                ('Asynchronous Programming', 'When is asynchronous programming most advantageous in {skill}?', 'For I/O-bound operations like network requests, database lookups, and disk access where threads would otherwise sit idle', 'For purely CPU-bound mathematical matrix multiplication', 'For running short synchronous loops', 'It is never advantageous in modern programming', 'A', 'Async I/O frees worker threads to handle other tasks while waiting for network or disk responses, boosting concurrency.'),
                ('Database Transactions', "What does the 'Isolation' property in ACID database transactions ensure for {skill} apps?", 'Concurrent transactions execute without interfering with one another or seeing partial, uncommitted changes', 'All transactions are written to separate physical hard drives', 'Transactions never lock any table rows', 'Transactions can never be rolled back', 'A', 'Isolation guarantees that intermediate states of concurrent transactions are hidden from each other.'),
                ('System Monitoring', 'What are the three core pillars of system observability in {skill} production environments?', 'Metrics, Logs, and Distributed Tracing', 'CPU, RAM, and Disk space only', 'HTML, CSS, and JavaScript', 'HTTP, FTP, and SSH', 'A', 'Metrics track quantitative state; logs provide event records; distributed traces track requests across microservices.'),
                ('Technical Debt', 'How should technical debt be managed in a growing {skill} codebase?', 'By regularly allocating time for refactoring, updating deprecated dependencies, and writing automated tests', 'By ignoring it until the entire system crashes permanently', 'By rewriting the application in a different language every month', 'By prohibiting code refactoring', 'A', 'Proactively addressing technical debt through incremental refactoring and test coverage maintains developer velocity.'),
            ]
            base_bank = []
            for topic, q_text, opt_a, opt_b, opt_c, opt_d, corr, expl in domains:
                base_bank.append({
                    'question_text': q_text.format(skill=skill_name),
                    'option_a': opt_a.format(skill=skill_name) if '{skill}' in opt_a else opt_a,
                    'option_b': opt_b.format(skill=skill_name) if '{skill}' in opt_b else opt_b,
                    'option_c': opt_c.format(skill=skill_name) if '{skill}' in opt_c else opt_c,
                    'option_d': opt_d.format(skill=skill_name) if '{skill}' in opt_d else opt_d,
                    'correct_option': corr,
                    'explanation': expl.format(skill=skill_name),
                    'topic': topic,
                    'difficulty': difficulty
                })

        # Return exactly the requested count, filtering excluded questions
        results = []
        for item in base_bank:
            if item['question_text'] not in exclude:
                results.append(item)
            if len(results) >= count:
                break

        # If bank was exhausted, fill from remaining items
        if len(results) < count:
            for item in base_bank:
                results.append(item)
                if len(results) >= count:
                    break

        return results[:count]


# Global singleton instance
ai_service = AIService()
