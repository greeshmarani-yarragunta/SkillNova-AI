# SkillNova AI 🚀
### AI-Powered Skill Assessment & Career Readiness Platform

[![React](https://img.shields.io/badge/Frontend-React_19_|_Vite-61DAFB?logo=react&logoColor=black)](https://reactjs.org/)
[![Django](https://img.shields.io/badge/Backend-Django_5.1_|_DRF-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![JWT](https://img.shields.io/badge/Auth-SimpleJWT_RBAC-black?logo=jsonwebtokens)](https://jwt.io/)
[![Database](https://img.shields.io/badge/Database-MySQL_|_SQLite_Fallback-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![AI Integration](https://img.shields.io/badge/AI-Google_Gemini_+_Deterministic_Engine-FF6F00?logo=google&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**SkillNova AI** is an enterprise-grade technical skill assessment and career readiness platform designed to help software engineers benchmark their real-world capabilities, pinpoint conceptual blind spots, practice realistic mock interviews, and optimize resumes for target engineering roles.

Built with **React 19**, **Django REST Framework (DRF)**, **MySQL**, and **Google Gemini AI**, the platform delivers adaptive AI diagnostics, question bank authoring, comprehensive score breakdown rings, actionable improvement pathways, and full historical performance auditing.

---

## 📑 Table of Contents
1. [Platform Core User Flow](#-core-user-flow)
2. [Core Features](#-core-features)
3. [Role-Based Access Control (RBAC)](#-role-based-access-control-rbac)
4. [System Architecture](#-system-architecture)
5. [Demo Accounts](#-demo-accounts)
6. [Technology Stack](#-technology-stack)
7. [REST API Directory](#-rest-api-directory)
8. [Local Setup & Installation](#-local-setup--installation)
9. [Testing & Verification](#-testing--verification)
10. [Visual Identity & Design System](#-visual-identity--design-system)

---

## 🎯 Core User Flow

The central experience of SkillNova AI guides candidates through an end-to-end diagnostic and improvement cycle:

```text
Login
  ↓
Student Dashboard
  ↓
Select Skill (Python, Django, React, SQL, etc.)
  ↓
Choose Difficulty (Beginner | Intermediate | Advanced)
  ↓
Choose Number of Questions (5 | 10 | 15)
  ↓
Start AI Assessment
  ↓
Answer Questions (Interactive Progress & Option Selection)
  ↓
Submit Test
  ↓
AI Diagnostic Evaluation
  ↓
Circular Visual Score Indicator & Level Classification
  ↓
Strong Topics (✓) vs. Needs Improvement (⚠)
  ↓
AI Recommendations & Educational Insights
  ↓
Assessment History & Continuous Benchmark Tracking
```

---

## 🌟 Core Features

### 🎓 1. Student Portal
* **Diagnostic Skill Assessments**: Choose from curated technical disciplines (Python, Django, JavaScript, React, SQL, HTML, CSS, REST APIs, Git, Data Structures, Machine Learning). Configure question counts (5, 10, or 15) and difficulty tiers (Beginner, Intermediate, Advanced).
* **Dynamic AI & Banked Questions**: Tests pull approved questions from the verified question bank or generate new questions dynamically via Google Gemini.
* **Assessment Results & Score Indicator**: Visual circular gauge displaying score percentage, assessed level (Beginner, Intermediate, Advanced, Expert), transparent estimation disclaimer, breakdown of strong areas, prioritized improvement topics, and actionable recommendations.
* **Assessment History**: Audit log of past attempts tracking skill, date, difficulty, score percentage, level badge, and weak topics with instant review links.
* **Student Dashboard**: Real-time KPI summary (Tests Taken, Average Score, Skills Assessed, Tests This Month), per-skill mastery progress bars, recent assessments table, recommended skills, and quick actions.
* **24/7 AI Learning Assistant**: Technical chat tutor providing clear explanations, mental models, syntax examples, and instant micro-practice checks without exposing backend API keys.
* **AI Mock Interview Preparation**: Role-focused interview simulations (Python Developer, Full Stack, Frontend, Backend, Data Scientist) generating technical, conceptual, scenario, project, and HR questions with constructive AI evaluations.
* **Resume Skill-Gap Analyzer**: Upload PDF resumes to extract technical competencies via `pypdf`, benchmark against target job descriptions, discover missing skills, and unlock suggested direct assessment links.

### 👨‍🏫 2. Instructor Assessment Studio
* **Instructor Dashboard**: Assessment-centric KPI cards (Total Questions in Bank, Total Platform Assessments, Active Skills, Student Attempts).
* **Question Bank Management**: Full CRUD interface for assessment questions with filtering by skill, difficulty, and approval status (`draft`, `approved`, `rejected`).
* **AI Question Generator**: Rapidly generate multiple-choice questions with 4 options, correct answer indices, explanations, and topic tags. Review and edit inline before publishing directly to the active test pool.
* **Student Performance Analytics**: Audit table showing individual student assessment attempts, scores, assigned levels, and weak topic clusters.

### 🛡️ 3. Admin Governance Center
* **Platform KPIs**: 6 core metrics tracking Total Users, Students, Instructors, Skills, Assessments Logged, and Question Bank Volume.
* **User Management Directory**: Search, filter by role, activate/deactivate accounts, and adjust permissions.
* **Skill Taxonomy Management**: Create, edit, and categorize technical domains, difficulty ratings, and topic tags.
* **Assessment Moderation**: Comprehensive audit log of all completed assessments across all candidates.

---

## 👥 Role-Based Access Control (RBAC)

SkillNova AI enforces strict permission boundaries on both the **Django REST API** (via `IsStudent`, `IsInstructor`, `IsAdmin`) and the **React Client** (via protected route guards):

| Feature / Resource | Student | Instructor | Admin |
| :--- | :---: | :---: | :---: |
| Take AI Assessments & View Results | ✅ | ❌ | ❌ |
| View Personal Assessment History | ✅ | ❌ | ❌ |
| AI Mock Interview & Resume Analyzer | ✅ | ❌ | ❌ |
| AI Technical Learning Assistant | ✅ | ✅ | ✅ |
| Manage Question Bank (Create / Edit / Delete) | ❌ | ✅ | ✅ |
| AI Question Generator Studio | ❌ | ✅ | ✅ |
| View Student Performance Breakdown | ❌ | ✅ | ✅ |
| Skill Taxonomy Management | ❌ | ❌ | ✅ |
| User Directory & Account Governance | ❌ | ❌ | ✅ |
| Platform-Wide System Analytics | ❌ | ❌ | ✅ |

---

## 🏛️ System Architecture

```text
                    SkillNova AI
                         |
        ┌────────────────┼────────────────┐
        |                |                |
   Assessments       AI Career         Skill Analysis
        |           Preparation           |
        |                |                |
   AI Tests        ┌─────┴─────┐       Skill Gaps
        |          |           |          |
   Score        Interview    Resume    Recommendations
        |
   Skill Level
        |
   Weak Topics
```

### Detailed Component Layout:

```text
               +---------------------------------------+
               |        React 19 + Vite Client         |
               |       Clean Modern SaaS Dashboard     |
               |      Deep Navy / Indigo / Cyan        |
               +-------------------+-------------------+
                                   |  JWT Bearer / JSON
                                   v
               +---------------------------------------+
               |      Django 5.1 / DRF API Gateway     |
               |      Role Permissions & Rate Limits   |
               +----+-------------+---------------+----+
                    |             |               |
        +-----------+             |               +-----------+
        v                         v                           v
+-----------------+      +-------------------+      +-------------------+
|  Accounts App   |      |  Assessments App  |      |      AI App       |
| Users, Profiles |      | Dynamic Tests,    |      | Question Bank,    |
| Skill Taxonomy  |      | Scoring, Results  |      | Gemini Engine,    |
| Audit Stats     |      | History Engine    |      | Mock Interviews   |
+-----------------+      +-------------------+      +-------------------+
        |                         |                           |
        +-----------+             |               +-----------+
                    |             |               |
                    v             v               v
               +---------------------------------------+
               |          AI & Heuristics Layer        |
               |   - Google Gemini Pro / Flash API     |
               |   - Deterministic Fallback Engine     |
               |   - PyPDF Resume Parsing Engine       |
               +-------------------+-------------------+
                                   |
                                   v
               +---------------------------------------+
               |        Database Layer (MySQL)         |
               |    Primary: MySQL 8.0+ (PyMySQL)      |
               |    Fallback: Automated SQLite3        |
               +---------------------------------------+
```

---

## 🔑 Demo Accounts

The system is pre-seeded with test accounts for each role:

| Role | Email | Password | Primary Portal |
| :--- | :--- | :--- | :--- |
| **Student** | `student@skillnova.ai` | `Student@123` | `/dashboard` (Assessments, History, AI Tutor, Interview, Resume) |
| **Instructor** | `instructor@skillnova.ai` | `Instructor@123` | `/instructor/dashboard` (Question Bank, Generator, Performance) |
| **Administrator** | `admin@skillnova.ai` | `Admin@123` | `/admin/dashboard` (Users, Skills, Assessment Logs, KPIs) |

---

## 🛠️ Technology Stack

### Frontend
* **Framework**: React 19 (SPA) with Vite build system
* **Routing**: React Router DOM (v7) with role-protected route guards
* **HTTP Client**: Axios with automated bearer tokens & refresh interceptors
* **Design System**: Vanilla CSS with customized CSS variables (Deep Navy, Indigo, Cyan, Slate)
* **Icons**: React Icons (`fi`)
* **Visual FX**: Canvas Confetti for assessment milestone celebrations

### Backend
* **Language & Framework**: Python 3.12, Django 5.1 / DRF
* **Authentication**: `djangorestframework-simplejwt`
* **Database Driver**: `PyMySQL`
* **CORS**: `django-cors-headers`
* **Resume Text Extraction**: `pypdf`
* **AI Service**: Google Gemini API (`google-generativeai`) with resilient heuristic engine fallback for 100% test reliability

### Database
* **Primary**: MySQL Server 8.0+
* **Fallback**: Automated SQLite3 configuration for local development

---

## 📡 REST API Directory

All API endpoints are mounted under `/api/`.

### 1. Authentication & Users (`accounts`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/api/auth/register/` | Register new user account | Public |
| `POST` | `/api/auth/login/` | JWT token acquisition (access + refresh) | Public |
| `POST` | `/api/auth/refresh/` | Refresh JWT access token | Public |
| `GET/PUT` | `/api/auth/profile/` | Fetch or update user profile | Authenticated |
| `GET` | `/api/skills/` | List all available technical skills | Public |
| `GET/POST`| `/api/student/skills/` | Manage student tracked skills | Student |
| `GET` | `/api/admin/users/` | Directory of platform users | Admin |
| `PATCH`| `/api/admin/users/<id>/` | Update user status or assign role | Admin |
| `GET` | `/api/admin/stats/` | Platform-wide assessment statistics | Admin |

### 2. Assessments & History (`assessments`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/api/assessments/generate/` | Generate test (checks Question Bank then AI) | Student |
| `GET` | `/api/assessments/<id>/` | Fetch assessment questions | Student |
| `POST` | `/api/assessments/<id>/submit/` | Submit answers and calculate score/level | Student |
| `GET` | `/api/assessments/results/` | Student assessment history & score records | Student |
| `GET` | `/api/assessments/roadmap/<id>/` | Fetch skill learning progression | Student |
| `GET` | `/api/assessments/admin/assessments/` | Global audit log of all test attempts | Admin |

### 3. AI Services & Question Bank (`ai`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/api/ai/ask/` | Ask AI technical tutor a question | Authenticated |
| `GET` | `/api/ai/chat-history/` | Fetch tutor conversation history | Authenticated |
| `POST` | `/api/ai/interview/generate/` | Generate mock technical interview session | Student |
| `GET` | `/api/ai/interview/<id>/` | Fetch interview question set | Student |
| `POST` | `/api/ai/interview/<id>/submit/` | Submit interview answers for AI scoring | Student |
| `POST` | `/api/ai/instructor-questions/generate/` | Generate questions using AI for bank | Instructor/Admin |
| `GET` | `/api/ai/instructor-questions/drafts/` | List and filter question bank items | Instructor/Admin |
| `POST` | `/api/ai/instructor-questions/drafts/` | Create a manual question in bank | Instructor/Admin |
| `POST` | `/api/ai/instructor-questions/<id>/approve/` | Approve question for student tests | Instructor/Admin |
| `PATCH` | `/api/ai/instructor-questions/<id>/` | Edit question content, options, answer | Instructor/Admin |
| `DELETE` | `/api/ai/instructor-questions/<id>/` | Delete question from question bank | Instructor/Admin |
| `GET` | `/api/ai/instructor/stats/` | Instructor question & assessment KPIs | Instructor/Admin |
| `GET` | `/api/ai/instructor/performance/` | Student test performance breakdown | Instructor/Admin |

### 4. Resume Analyzer (`resumes`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/api/resumes/analyze/` | Upload PDF resume for skill-gap audit | Student |
| `GET` | `/api/resumes/history/` | List student resume audit history | Student |
| `GET` | `/api/resumes/<id>/` | Get detailed matched vs. missing skills | Student |

### 5. Notifications (`notifications`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `GET` | `/api/notifications/` | List user notifications | Authenticated |
| `GET` | `/api/notifications/unread-count/` | Badge count of unread notifications | Authenticated |
| `POST` | `/api/notifications/<id>/read/` | Mark single notification as read | Authenticated |
| `POST` | `/api/notifications/mark-all-read/` | Mark all notifications as read | Authenticated |

---

## 💻 Local Setup & Installation

### Prerequisites
* **Python**: 3.10, 3.11, or 3.12
* **Node.js**: 18.x or 20.x + `npm`
* **MySQL** (Optional): SQLite fallback activates automatically if MySQL is offline.

### 1. Clone & Workspace Setup
```bash
git clone https://github.com/your-username/skillnova-ai.git
cd "SkillNova AI"
```

### 2. Backend Setup
1. Activate virtual environment:
   ```bash
   # Windows PowerShell
   python -m venv backend\venv
   .\backend\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv backend/venv
   source backend/venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install django djangorestframework djangorestframework-simplejwt django-cors-headers pymysql python-dotenv pypdf requests google-generativeai
   ```

3. Configure Environment Variables (`backend/.env`):
   ```env
   SECRET_KEY=django-insecure-skillnova-ai-assessment-platform-secret
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # MySQL Database (Gracefully falls back to SQLite if unreachable)
   DB_NAME=skillnova_db
   DB_USER=root
   DB_PASSWORD=your_password
   DB_HOST=127.0.0.1
   DB_PORT=3306

   # CORS
   CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174

   # Google Gemini Key (Optional; built-in heuristic fallback runs if omitted)
   GEMINI_API_KEY=
   ```

4. Run Migrations & Seed Demo Data:
   ```bash
   python backend/manage.py migrate
   python backend/manage.py seed_data
   ```

5. Start the Django REST Backend:
   ```bash
   python backend/manage.py runserver 127.0.0.1:8008
   ```

### 3. Frontend Setup
1. Open a terminal in `frontend`:
   ```bash
   cd frontend
   npm install
   ```

2. Configure `frontend/.env`:
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8008/api
   ```

3. Start Frontend Development Server:
   ```bash
   npm run dev -- --port 5174
   ```
   *Access the application at `http://localhost:5174/`.*

---

## 🧪 Testing & Verification

### Running Backend Unit Tests
Execute the comprehensive test suite verifying authentication, assessment generation, question bank sampling, submission scoring, AI tutor, and instructor question moderation:
```bash
python backend/manage.py test accounts assessments ai
```
*Expected Output:*
```text
Ran 12 tests in ~14s
OK
```

### Running Frontend Production Build
Validate all React 19 JSX components, routing, and asset compilation:
```bash
cd frontend
npm run build
```
*Expected Output:*
```text
✓ built in ~1s (0 errors)
```

---

## 🎨 Visual Identity & Design System

SkillNova AI uses a professional **Deep Navy + Teal + Cyan** design system:

### Dark Mode
* **Background**: `#07111F` (Deep Navy)
* **Secondary Background**: `#0B1726`
* **Sidebar**: `#0A1422`
* **Card & Surface Background**: `#101F32`
* **Card Hover**: `#14283D`
* **Borders**: `#20354A`
* **Primary Teal**: `#14B8A6` (Primary action buttons, active navigation, focus indicators)
* **Primary Hover**: `#0D9488`
* **Secondary Cyan**: `#22D3EE` (Progress meters, badges, and secondary highlights)
* **Light Accent**: `#67E8F9`
* **Main Text**: `#F8FAFC`
* **Secondary Text**: `#CBD5E1`
* **Muted Text**: `#94A3B8`
* **Success / Warning / Error**: `#22C55E` / `#F59E0B` / `#EF4444`

### Light Mode
* **Background**: `#F4F7FA`
* **Secondary Background**: `#EAF0F5`
* **Sidebar & Cards**: `#FFFFFF`
* **Card Hover**: `#F1F5F9`
* **Borders**: `#D8E1EA`
* **Primary Teal**: `#0F766E`
* **Primary Hover**: `#115E59`
* **Secondary Cyan**: `#0891B2`
* **Main Text**: `#0F172A`
* **Secondary Text**: `#334155`
* **Muted Text**: `#64748B`
* **Success / Warning / Error**: `#16A34A` / `#D97706` / `#DC2626`

---

## 📄 License
This project is open-source and distributed under the [MIT License](LICENSE).
