from django.urls import path
from .views import (
    AIAskAssistantView, AIChatHistoryView,
    AIInterviewGenerateView, AIInterviewSubmitView,
    AIInterviewHistoryView, AIInterviewDetailView,
    InstructorGenerateQuestionsView, InstructorDraftQuestionsView,
    InstructorStatsView, InstructorStudentPerformanceView
)

urlpatterns = [
    # AI Learning Assistant Chat
    path('ai/ask/', AIAskAssistantView.as_view(), name='ai_ask'),
    path('ai/chat-history/', AIChatHistoryView.as_view(), name='ai_chat_history'),

    # AI Mock Interview Prep
    path('ai/interview/generate/', AIInterviewGenerateView.as_view(), name='ai_interview_generate'),
    path('ai/interview/history/', AIInterviewHistoryView.as_view(), name='ai_interview_history'),
    path('ai/interview/<int:pk>/', AIInterviewDetailView.as_view(), name='ai_interview_detail'),
    path('ai/interview/<int:pk>/submit/', AIInterviewSubmitView.as_view(), name='ai_interview_submit'),

    # Instructor Question Bank & Generation
    path('ai/instructor-questions/generate/', InstructorGenerateQuestionsView.as_view(), name='ai_instructor_generate'),
    path('ai/instructor-questions/', InstructorDraftQuestionsView.as_view(), name='ai_instructor_drafts'),
    path('ai/instructor-questions/<int:pk>/', InstructorDraftQuestionsView.as_view(), name='ai_instructor_draft_detail'),
    path('ai/instructor-questions/<int:pk>/approve/', InstructorDraftQuestionsView.as_view(), name='ai_instructor_approve'),

    # Instructor Assessment Management & Stats
    path('instructor/stats/', InstructorStatsView.as_view(), name='instructor_stats'),
    path('instructor/performance/', InstructorStudentPerformanceView.as_view(), name='instructor_performance'),
    path('instructor/questions/', InstructorDraftQuestionsView.as_view(), name='instructor_questions_alias'),
    path('instructor/questions/<int:pk>/', InstructorDraftQuestionsView.as_view(), name='instructor_question_detail_alias'),
    path('instructor/questions/<int:pk>/approve/', InstructorDraftQuestionsView.as_view(), name='instructor_question_approve_alias'),
]
