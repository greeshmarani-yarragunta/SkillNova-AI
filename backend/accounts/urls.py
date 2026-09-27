from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, ProfileView,
    SkillListView, SkillDetailView,
    StudentSkillListCreateView,
    AdminUserListView, AdminUserDetailView, AdminCreateInstructorView, AdminPlatformStatsView
)

urlpatterns = [
    # Authentication
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),

    # Skills System
    path('skills/', SkillListView.as_view(), name='skills_list'),
    path('skills/<int:pk>/', SkillDetailView.as_view(), name='skill_detail'),
    path('student/skills/', StudentSkillListCreateView.as_view(), name='student_skills'),
    path('student/skills/<int:pk>/', StudentSkillListCreateView.as_view(), name='student_skill_detail'),

    # Admin Management
    path('admin/users/', AdminUserListView.as_view(), name='admin_users'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('admin/instructors/', AdminCreateInstructorView.as_view(), name='admin_create_instructor'),
    path('admin/stats/', AdminPlatformStatsView.as_view(), name='admin_stats'),
]
