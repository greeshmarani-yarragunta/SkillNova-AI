from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'STUDENT')


class IsInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and (
                request.user.role == 'INSTRUCTOR' or request.user.role == 'ADMIN' or request.user.is_superuser
            )
        )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and (
                request.user.role == 'ADMIN' or request.user.is_superuser
            )
        )


class IsOwnerOrInstructorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['ADMIN'] or request.user.is_superuser:
            return True
        if hasattr(obj, 'instructor'):
            return obj.instructor == request.user
        if hasattr(obj, 'student'):
            return obj.student == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class CanViewAssessmentResult(permissions.BasePermission):
    """
    Permission to view assessment results:
    - Admin: can view all assessment results.
    - Instructor: can view student assessment results.
    - Student: can only view their own assessment results.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Admin can view all assessments
        if user.role == 'ADMIN' or user.is_superuser:
            return True

        # Instructor can view student assessments (or their own)
        if user.role == 'INSTRUCTOR':
            if hasattr(obj, 'student'):
                return obj.student.role == 'STUDENT' or obj.student == user
            return True

        # Student can only view their own assessment
        if user.role == 'STUDENT':
            if hasattr(obj, 'student'):
                return obj.student == user
            if hasattr(obj, 'user'):
                return obj.user == user
            return False

        return False

