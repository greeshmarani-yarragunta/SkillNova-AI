import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';

// Layouts
import MainLayout from './layouts/MainLayout';
import DashboardLayout from './layouts/DashboardLayout';
import ProtectedRoute from './components/ProtectedRoute';
import ScrollToTop from './components/ScrollToTop';

// Public Pages
import LandingPage from './pages/public/LandingPage';
import LoginPage from './pages/public/LoginPage';
import SignupPage from './pages/public/SignupPage';
import AboutPage from './pages/public/AboutPage';
import ContactPage from './pages/public/ContactPage';

// Shared / Discovery Pages
import SkillsPage from './pages/student/SkillsPage';
import ProfilePage from './pages/student/ProfilePage';
import NotificationsPage from './pages/student/NotificationsPage';

// Student Assessment & AI Career Readiness Pages
import StudentDashboard from './pages/student/StudentDashboard';
import SkillAssessmentPage from './pages/student/SkillAssessmentPage';
import AssessmentResultPage from './pages/student/AssessmentResultPage';
import AssessmentHistoryPage from './pages/student/AssessmentHistoryPage';
import AIAssistantPage from './pages/student/AIAssistantPage';
import InterviewPrepPage from './pages/student/InterviewPrepPage';
import ResumeAnalyzerPage from './pages/student/ResumeAnalyzerPage';

// Instructor Assessment & Question Bank Pages
import InstructorDashboard from './pages/instructor/InstructorDashboard';
import InstructorQuestionsPage from './pages/instructor/InstructorQuestionsPage';
import AIQuestionGeneratorPage from './pages/instructor/AIQuestionGeneratorPage';
import StudentPerformancePage from './pages/instructor/StudentPerformancePage';

// Admin Platform Governance Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import UsersManagementPage from './pages/admin/UsersManagementPage';
import SkillsManagementPage from './pages/admin/SkillsManagementPage';
import AssessmentsManagementPage from './pages/admin/AssessmentsManagementPage';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <ScrollToTop />
          <Routes>
            {/* Public Layout */}
            <Route element={<MainLayout />}>
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignupPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/contact" element={<ContactPage />} />
            </Route>

            {/* Dashboard Layout for Authenticated Users */}
            <Route
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              {/* Shared App Views */}
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/notifications" element={<NotificationsPage />} />

              {/* Student Routes */}
              <Route path="/dashboard" element={<StudentDashboard />} />
              <Route
                path="/skills"
                element={
                  <ProtectedRoute allowedRoles={['STUDENT', 'ADMIN']}>
                    <SkillsPage />
                  </ProtectedRoute>
                }
              />
              <Route path="/assessments" element={<SkillAssessmentPage />} />
              <Route path="/assessments/new" element={<SkillAssessmentPage />} />
              <Route path="/assessments/:id" element={<AssessmentResultPage />} />
              <Route path="/assessment-history" element={<AssessmentHistoryPage />} />
              <Route path="/roadmap" element={<Navigate to="/dashboard" replace />} />
              <Route path="/ai-assistant" element={<AIAssistantPage />} />
              <Route path="/interview-prep" element={<InterviewPrepPage />} />
              <Route path="/resume-analyzer" element={<ResumeAnalyzerPage />} />

              {/* Instructor Routes */}
              <Route
                path="/instructor/dashboard"
                element={
                  <ProtectedRoute allowedRoles={['INSTRUCTOR', 'ADMIN']}>
                    <InstructorDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/instructor/questions"
                element={
                  <ProtectedRoute allowedRoles={['INSTRUCTOR', 'ADMIN']}>
                    <InstructorQuestionsPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/instructor/ai-questions"
                element={
                  <ProtectedRoute allowedRoles={['INSTRUCTOR', 'ADMIN']}>
                    <AIQuestionGeneratorPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/instructor/performance"
                element={
                  <ProtectedRoute allowedRoles={['INSTRUCTOR', 'ADMIN']}>
                    <StudentPerformancePage />
                  </ProtectedRoute>
                }
              />

              {/* Admin Routes */}
              <Route
                path="/admin/dashboard"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN']}>
                    <AdminDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/users"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN']}>
                    <UsersManagementPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/skills"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN']}>
                    <SkillsManagementPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/assessments"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN']}>
                    <AssessmentsManagementPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/questions"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN']}>
                    <InstructorQuestionsPage />
                  </ProtectedRoute>
                }
              />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
