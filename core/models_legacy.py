from django.db import models
from django.conf import settings

class District(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class University(models.Model):
    name = models.CharField(max_length=255, unique=True)
    state = models.CharField(max_length=100, default="Kerala")

    def __str__(self):
        return self.name

class College(models.Model):
    COLLEGE_TYPES = [
        ('government', 'Government'),
        ('aided', 'Aided'),
        ('private', 'Private Self-Financing'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='college_profile_core')
    name = models.CharField(max_length=255)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, related_name='colleges')
    address = models.TextField(null=True, blank=True)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, related_name='colleges')
    year_established = models.PositiveIntegerField(null=True, blank=True)
    college_type = models.CharField(max_length=50, choices=COLLEGE_TYPES, default='private')
    website = models.URLField(null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)

    @property
    def place(self):
        return self.district.name if self.district else ""

    @property
    def Type(self):
        return self.get_college_type_display()

    @property
    def cut_off_mark(self):
        # Default to a general cutoff or from courses
        return self.offered_courses.first().cutoff_marks if self.offered_courses.exists() else 0

    @property
    def Description(self):
        return self.address or f"{self.name} is a {self.college_type} college in {self.place}."

    def __str__(self):
        return self.name

class Course(models.Model):
    LEVEL_CHOICES = [
        ('UG', 'Undergraduate'),
        ('PG', 'Postgraduate'),
        ('Diploma', 'Diploma'),
        ('Certificate', 'Certificate'),
    ]
    STREAM_CHOICES = [
        ('Science', 'Science'),
        ('Commerce', 'Commerce'),
        ('Arts', 'Arts'),
        ('Professional', 'Professional'),
        ('Other', 'Other'),
    ]
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    duration = models.CharField(max_length=50, help_text="e.g., 3 Years, 4 Years")
    stream = models.CharField(max_length=50, choices=STREAM_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.level})"

class CollegeCourse(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='offered_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='colleges_offering')
    cutoff_marks = models.FloatField(null=True, blank=True)
    intake_capacity = models.PositiveIntegerField(null=True, blank=True)
    fees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    eligibility = models.TextField(null=True, blank=True)

    @property
    def Courses(self):
        return self.course.name

    class Meta:
        unique_together = ('college', 'course')

    def __str__(self):
        return f"{self.course.name} at {self.college.name}"

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='extended_profile')
    name = models.CharField(max_length=255)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    preferred_stream = models.CharField(max_length=50, choices=Course.STREAM_CHOICES, null=True, blank=True)
    interests = models.TextField(help_text="Comma separated interests", null=True, blank=True)
    skills = models.TextField(help_text="Comma separated skills", null=True, blank=True)
    marks_12th = models.FloatField(null=True, blank=True)
    subjects_12th = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class LegacyAptitudeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class LegacyAptitudeQuestion(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    question_text = models.TextField()
    category = models.ForeignKey(LegacyAptitudeCategory, on_delete=models.CASCADE, related_name='questions')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')

    def __str__(self):
        return f"[{self.category.name}] {self.question_text[:50]}"

class LegacyAptitudeAnswer(models.Model):
    question = models.ForeignKey(LegacyAptitudeQuestion, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer_text

class LegacyAptitudeResult(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='test_results')
    score = models.FloatField()
    category_scores = models.JSONField(help_text="Stores score per category")
    recommended_stream = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.student.name} - {self.score}"

class CareerPath(models.Model):
    career_name = models.CharField(max_length=255)
    required_skills = models.TextField()
    required_courses = models.TextField()
    description = models.TextField()

    def __str__(self):
        return self.career_name
