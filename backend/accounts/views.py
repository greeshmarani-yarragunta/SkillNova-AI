from rest_framework import status, generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg

from .models import User, StudentProfile, InstructorProfile, Skill, StudentSkill
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    StudentProfileSerializer, InstructorProfileSerializer,
    SkillSerializer, StudentSkillSerializer, AdminCreateInstructorSerializer
)
from .permissions import IsAdmin, IsStudent


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        role_attempt = request.data.get('role')
        if role_attempt and str(role_attempt).strip().upper() != 'STUDENT':
            return Response(
                {
                    'error': 'Direct registration as an Instructor or Admin is prohibited.',
                    'detail': 'Public registration is restricted to Student accounts only. Instructor accounts must be created by an administrator.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'Registration successful! You can now log in.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        data = request.data

        # Explicitly disallow role modification / privilege escalation
        if 'role' in data and data['role'] != user.role:
            return Response(
                {'error': 'Role modification is not permitted. Contact an administrator.'},
                status=status.HTTP_403_FORBIDDEN
            )
        if 'is_staff' in data or 'is_superuser' in data:
            return Response(
                {'error': 'Privilege escalation attempt rejected.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update core user fields
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.phone = data.get('phone', user.phone)
        user.bio = data.get('bio', user.bio)
        user.avatar = data.get('avatar', user.avatar)
        user.save()

        # Update role-specific profile
        if user.is_student:
            profile, _ = StudentProfile.objects.get_or_create(user=user)
            if 'student_profile' in data:
                sp_data = data['student_profile']
                profile.current_education = sp_data.get('current_education', profile.current_education)
                profile.target_role = sp_data.get('target_role', profile.target_role)
                profile.experience_level = sp_data.get('experience_level', profile.experience_level)
                profile.github_url = sp_data.get('github_url', profile.github_url)
                profile.linkedin_url = sp_data.get('linkedin_url', profile.linkedin_url)
                profile.save()
        elif user.is_instructor:
            profile, _ = InstructorProfile.objects.get_or_create(user=user)
            if 'instructor_profile' in data:
                ip_data = data['instructor_profile']
                profile.title = ip_data.get('title', profile.title)
                profile.organization = ip_data.get('organization', profile.organization)
                profile.expertise = ip_data.get('expertise', profile.expertise)
                profile.save()

        return Response(UserSerializer(user).data)

    def patch(self, request):
        return self.put(request)


class SkillListView(generics.ListCreateAPIView):
    queryset = Skill.objects.all().order_by('name')
    serializer_class = SkillSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [AllowAny()]


class SkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdmin()]
        return [AllowAny()]


class StudentSkillListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        skills = StudentSkill.objects.filter(student=request.user).select_related('skill')
        serializer = StudentSkillSerializer(skills, many=True)
        return Response(serializer.data)

    def post(self, request):
        skill_id = request.data.get('skill_id')
        if not skill_id:
            return Response({'error': 'skill_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        skill = get_object_or_404(Skill, id=skill_id)
        student_skill, created = StudentSkill.objects.get_or_create(
            student=request.user,
            skill=skill,
            defaults={
                'proficiency_level': request.data.get('proficiency_level', 'Beginner'),
                'progress_percentage': request.data.get('progress_percentage', 10),
            }
        )
        if not created:
            if 'proficiency_level' in request.data:
                student_skill.proficiency_level = request.data['proficiency_level']
            if 'progress_percentage' in request.data:
                student_skill.progress_percentage = request.data['progress_percentage']
            student_skill.save()

        return Response(StudentSkillSerializer(student_skill).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, pk=None):
        if not pk:
            skill_id = request.data.get('skill_id')
            student_skill = get_object_or_404(StudentSkill, student=request.user, skill_id=skill_id)
        else:
            student_skill = get_object_or_404(StudentSkill, id=pk, student=request.user)
        student_skill.delete()
        return Response({'message': 'Skill removed from your learning list.'}, status=status.HTTP_204_NO_CONTENT)


class AdminCreateInstructorView(generics.CreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminCreateInstructorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'Instructor account created successfully.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class AdminUserListView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer

    def get_queryset(self):
        role_filter = self.request.query_params.get('role')
        search = self.request.query_params.get('search')
        qs = User.objects.all().order_by('-created_at')
        if role_filter:
            qs = qs.filter(role=role_filter)
        if search:
            qs = qs.filter(email__icontains=search) | qs.filter(username__icontains=search)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = AdminCreateInstructorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        user = self.get_object()

        # Prevent admin self-deactivation
        if user == request.user and 'is_active' in request.data:
            val = request.data['is_active']
            is_deactivating = str(val).lower() in ('false', '0') if isinstance(val, (str, int)) else not bool(val)
            if is_deactivating:
                return Response(
                    {'error': 'You cannot deactivate your own admin account.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        save_fields = []
        if 'is_active' in request.data:
            val = request.data['is_active']
            if isinstance(val, str):
                user.is_active = val.lower() in ('true', '1', 't')
            else:
                user.is_active = bool(val)
            save_fields.append('is_active')

        if 'role' in request.data:
            new_role = request.data['role']
            if new_role in ['STUDENT', 'INSTRUCTOR', 'ADMIN']:
                user.role = new_role
                save_fields.append('role')
                if new_role == 'INSTRUCTOR':
                    InstructorProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            'title': 'Technical Instructor',
                            'organization': 'SkillNova Academy',
                            'expertise': 'Software Engineering',
                            'verified': True
                        }
                    )
                elif new_role == 'STUDENT':
                    StudentProfile.objects.get_or_create(user=user)

        if save_fields:
            user.save(update_fields=save_fields)
        else:
            user.save()

        return Response(UserSerializer(user).data)


class AdminPlatformStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from assessments.models import Assessment, AssessmentQuestion
        from ai.models import AIGeneratedQuestionBank

        total_users = User.objects.count()
        total_students = User.objects.filter(role='STUDENT').count()
        total_instructors = User.objects.filter(role='INSTRUCTOR').count()
        total_skills = Skill.objects.count()
        total_assessments = Assessment.objects.count()
        total_questions = AssessmentQuestion.objects.count() + AIGeneratedQuestionBank.objects.count()
        test_attempts = Assessment.objects.filter(is_completed=True).count()
        avg_assessment_score = Assessment.objects.filter(is_completed=True).aggregate(Avg('percentage'))['percentage__avg'] or 0.0

        return Response({
            'total_users': total_users,
            'total_students': total_students,
            'total_instructors': total_instructors,
            'total_skills': total_skills,
            'total_assessments': total_assessments,
            'total_questions': total_questions,
            'test_attempts': test_attempts,
            'avg_assessment_score': round(avg_assessment_score, 1),
        })
