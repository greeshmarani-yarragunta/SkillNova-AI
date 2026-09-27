import re
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.text import slugify
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, StudentProfile, InstructorProfile, Skill, StudentSkill


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'current_education', 'target_role', 'experience_level',
            'github_url', 'linkedin_url', 'streak_days', 'points'
        ]


class InstructorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorProfile
        fields = ['id', 'title', 'organization', 'expertise', 'verified']


class UserSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(read_only=True)
    instructor_profile = InstructorProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'is_active', 'phone', 'avatar', 'bio', 'student_profile', 'instructor_profile',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.CharField(required=False, default='STUDENT')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'role', 'first_name', 'last_name']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email address already exists.")
        return value.lower()

    def validate_role(self, value):
        if value:
            norm_val = str(value).strip().upper()
            if norm_val != 'STUDENT':
                raise serializers.ValidationError(
                    "Public registration is only allowed for student accounts. "
                    "Instructor accounts must be created by an administrator."
                )
        return 'STUDENT'

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match."})

        # Explicitly verify initial data to block any attempt to pass non-student role
        role_submitted = self.initial_data.get('role')
        if role_submitted and str(role_submitted).strip().upper() != 'STUDENT':
            raise serializers.ValidationError({
                "role": "Public registration is only allowed for student accounts. "
                        "Instructor accounts must be created by an administrator."
            })
        attrs['role'] = 'STUDENT'
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        validated_data['role'] = 'STUDENT'
        password = validated_data.pop('password')
        username = validated_data.get('username') or validated_data['email'].split('@')[0]
        validated_data['username'] = username

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        StudentProfile.objects.get_or_create(user=user)
        return user


def generate_unique_username(email, base_name=None):
    if base_name and str(base_name).strip():
        raw = str(base_name).strip()
    elif email and '@' in email:
        raw = email.split('@')[0].strip()
    else:
        raw = 'instructor'

    base = re.sub(r'[^a-zA-Z0-9_]', '', raw.replace('.', '_').replace('-', '_'))
    if not base:
        base = 'instructor'

    candidate = base
    counter = 1
    while User.objects.filter(username__iexact=candidate).exists():
        candidate = f"{base}{counter}"
        counter += 1
    return candidate


class AdminCreateInstructorSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[])
    username = serializers.CharField(required=False, allow_blank=True, default='')
    password = serializers.CharField(write_only=True, min_length=6)
    title = serializers.CharField(required=False, default='Lead Technical Instructor')
    organization = serializers.CharField(required=False, default='SkillNova Academy')
    expertise = serializers.CharField(required=False, default='Full Stack Web Development, Python, Cloud Systems')

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'password', 'phone', 'bio', 'title', 'organization', 'expertise'
        ]
        read_only_fields = ['id']

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email address is required.")
        norm_email = value.lower().strip()
        if User.objects.filter(email__iexact=norm_email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return norm_email

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        if not email:
            raise serializers.ValidationError({"email": "Email address is required."})

        username = attrs.get('username')
        if not username or not str(username).strip():
            attrs['username'] = generate_unique_username(email)
        else:
            cleaned_username = str(username).strip()
            if User.objects.filter(username__iexact=cleaned_username).exists():
                attrs['username'] = generate_unique_username(email, base_name=cleaned_username)
            else:
                attrs['username'] = cleaned_username
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        title = validated_data.pop('title', 'Lead Technical Instructor')
        organization = validated_data.pop('organization', 'SkillNova Academy')
        expertise = validated_data.pop('expertise', 'Full Stack Web Development, Python, Cloud Systems')

        email = validated_data.get('email', '').strip().lower()
        username = validated_data.get('username')
        if not username or not str(username).strip():
            username = generate_unique_username(email)
        validated_data['username'] = username
        validated_data['role'] = 'INSTRUCTOR'
        validated_data['is_active'] = True

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        InstructorProfile.objects.create(
            user=user,
            title=title,
            organization=organization,
            expertise=expertise,
            verified=True
        )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').lower()
        password = attrs.get('password')

        user = authenticate(username=email, password=password)
        if not user:
            # Fallback to check if username was entered instead of email
            try:
                user_obj = User.objects.get(email=email)
                if user_obj.check_password(password):
                    user = user_obj
            except User.DoesNotExist:
                pass

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")

        refresh = RefreshToken.for_user(user)

        return {
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'slug', 'category', 'difficulty', 'description', 'topics', 'icon', 'created_at']


class StudentSkillSerializer(serializers.ModelSerializer):
    skill_details = SkillSerializer(source='skill', read_only=True)

    class Meta:
        model = StudentSkill
        fields = [
            'id', 'student', 'skill', 'skill_details',
            'proficiency_level', 'progress_percentage',
            'assessment_score', 'last_assessed', 'created_at'
        ]
        read_only_fields = ['id', 'student', 'created_at']
