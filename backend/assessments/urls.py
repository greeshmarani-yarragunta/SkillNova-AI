from django.urls import path
from .views import (
    GenerateAssessmentView, SubmitAssessmentView,
    AssessmentResultsListView, AssessmentDetailView,
    PersonalizedRoadmapView, AdminAssessmentManagementView
)

urlpatterns = [
    path('assessments/generate/', GenerateAssessmentView.as_view(), name='assessment_generate'),
    path('assessments/results/', AssessmentResultsListView.as_view(), name='assessment_results'),
    path('assessments/<int:pk>/', AssessmentDetailView.as_view(), name='assessment_detail'),
    path('assessments/<int:pk>/submit/', SubmitAssessmentView.as_view(), name='assessment_submit'),
    path('assessments/roadmap/<int:skill_id>/', PersonalizedRoadmapView.as_view(), name='assessment_roadmap'),
    path('admin/assessments/', AdminAssessmentManagementView.as_view(), name='admin_assessments'),
]
