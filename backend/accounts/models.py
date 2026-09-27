from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class User(AbstractUser):
    ROLE_CHOICES = (
        ('STUDENT', 'Student'),
        ('INSTRUCTOR', 'Instructor'),
        ('ADMIN', 'Admin'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    phone = models.CharField(max_length=25, blank=True, null=True)
    avatar = models.CharField(
        max_length=500,
        blank=True,
        default='https://api.dicebear.com/7.x/avataaars/svg?seed=SkillNova'
    )
    bio = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def is_student(self):
        return self.role == 'STUDENT'

    @property
    def is_instructor(self):
        return self.role == 'INSTRUCTOR'

    @property
    def is_platform_admin(self):
        return self.role == 'ADMIN' or self.is_superuser

    def __str__(self):
        return f"{self.email} ({self.role})"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    current_education = models.CharField(max_length=150, blank=True, default='Computer Science / IT')
    target_role = models.CharField(max_length=150, default='Full Stack Developer')
    experience_level = models.CharField(max_length=50, default='Fresher')
    github_url = models.URLField(blank=True, default='')
    linkedin_url = models.URLField(blank=True, default='')
    streak_days = models.PositiveIntegerField(default=1)
    points = models.PositiveIntegerField(default=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"StudentProfile: {self.user.email}"


class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    title = models.CharField(max_length=150, default='Lead Technical Instructor')
    organization = models.CharField(max_length=150, blank=True, default='SkillNova Academy')
    expertise = models.TextField(blank=True, default='Full Stack Web Development, Python, Cloud Systems')
    verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"InstructorProfile: {self.user.email}"


class Skill(models.Model):
    CATEGORY_CHOICES = (
        ('Programming', 'Programming Languages'),
        ('Framework', 'Frameworks & Libraries'),
        ('Database', 'Databases & Querying'),
        ('Core CS', 'Core Computer Science'),
        ('AI/ML', 'Artificial Intelligence & ML'),
        ('DevOps', 'DevOps & Tools'),
    )

    DIFFICULTY_CHOICES = (
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    )

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Programming')
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES, default='Beginner')
    description = models.TextField()
    topics = models.JSONField(default=list, help_text="List of curriculum topics for this skill")
    icon = models.CharField(max_length=50, default='FaCode')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class StudentSkill(models.Model):
    PROFICIENCY_CHOICES = (
        ('Beginner', 'Beginner (0-40%)'),
        ('Intermediate', 'Intermediate (41-75%)'),
        ('Advanced', 'Advanced (76-90%)'),
        ('Proficient', 'Proficient (91-100%)'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='enrolled_students')
    proficiency_level = models.CharField(max_length=50, choices=PROFICIENCY_CHOICES, default='Beginner')
    progress_percentage = models.PositiveIntegerField(default=0)
    assessment_score = models.FloatField(default=0.0)
    last_assessed = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'skill')

    def __str__(self):
        return f"{self.student.email} - {self.skill.name} ({self.progress_percentage}%)"
