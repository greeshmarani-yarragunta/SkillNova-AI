from django.urls import path
from .views import ResumeAnalyzeView, ResumeHistoryListView, ResumeDetailView

urlpatterns = [
    path('resumes/analyze/', ResumeAnalyzeView.as_view(), name='resume_analyze'),
    path('resumes/history/', ResumeHistoryListView.as_view(), name='resume_history'),
    path('resumes/<int:pk>/', ResumeDetailView.as_view(), name='resume_detail'),
]
