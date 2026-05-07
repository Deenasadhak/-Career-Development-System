from django.db import models
from django.conf import settings
from django.utils import timezone
from .taxonomy import Stream

class AptitudeCategory(models.Model):
    LOGICAL = 'LOGICAL'
    QUANTITATIVE = 'QUANTITATIVE'
    VERBAL = 'VERBAL'
    TECHNICAL = 'TECHNICAL'
    ARTS = 'ARTS'
    PERSONALITY = 'PERSONALITY'
    INTEREST = 'INTEREST'
    VALUES = 'VALUES'

    CODE_CHOICES = [
        (LOGICAL, 'Logical Reasoning'),
        (QUANTITATIVE, 'Quantitative Aptitude'),
        (VERBAL, 'Verbal Ability'),
        (TECHNICAL, 'Technical/ICT'),
        (ARTS, 'Aesthetic/Creative'),
        (PERSONALITY, 'Personality (Big Five)'),
        (INTEREST, 'Interest (RIASEC)'),
        (VALUES, 'Work Values'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, choices=CODE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    maps_to_streams = models.ManyToManyField(Stream, blank=True, related_name='aptitude_categories')

    class Meta:
        verbose_name = "Aptitude Category"
        verbose_name_plural = "Aptitude Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class AptitudeQuestion(models.Model):
    TYPE_CHOICES = [
        ('MCQ', 'Multiple Choice Question'),
        ('LIKERT', 'Likert Scale (1-5)'),
        ('RANKING', 'Ranking Item'),
        ('SCENARIO', 'Situational/Scenario Base'),
    ]
    DIFFICULTY_CHOICES = [
        ('E', 'Easy'),
        ('M', 'Medium'),
        ('H', 'Hard'),
    ]

    category = models.ForeignKey(AptitudeCategory, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='MCQ')
    difficulty = models.CharField(max_length=1, choices=DIFFICULTY_CHOICES, default='M')
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    time_limit_seconds = models.PositiveIntegerField(default=60)
    marks = models.PositiveIntegerField(default=1)
    explanation = models.TextField(blank=True)
    topic_tag = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Analytics
    times_used = models.PositiveIntegerField(default=0)
    correct_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Aptitude Question"
        verbose_name_plural = "Aptitude Questions"
        indexes = [
            models.Index(fields=['category', 'difficulty', 'is_active']),
        ]

    def __str__(self):
        return f"[{self.category.code}] {self.question_text[:50]}..."

class QuestionOption(models.Model):
    question = models.ForeignKey(AptitudeQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    riasec_code = models.CharField(max_length=1, blank=True) # R, I, A, S, E, C
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Question Option"
        verbose_name_plural = "Question Options"
        ordering = ['order']

    def __str__(self):
        return f"{self.option_text[:30]} (Correct: {self.is_correct})"

class TestSession(models.Model):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('ABANDONED', 'Abandoned'),
        ('EXPIRED', 'Expired'),
    ]
    TYPE_CHOICES = [
        ('FULL', 'Full Assessment'),
        ('QUICK', 'Quick Check'),
        ('PERSONALITY', 'Personality Test'),
        ('INTEREST', 'Interest Inventory'),
        ('VALUES', 'Work Values Assessment'),
    ]

    student = models.ForeignKey('core.StudentProfile', on_delete=models.CASCADE, related_name='test_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    test_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='FULL')
    total_time_seconds = models.PositiveIntegerField(null=True, blank=True)

    # Normalized Scores (0-100)
    logical_score = models.FloatField(default=0)
    quantitative_score = models.FloatField(default=0)
    verbal_score = models.FloatField(default=0)
    technical_score = models.FloatField(default=0)
    arts_score = models.FloatField(default=0)

    # Complex Profiles
    personality_profile = models.JSONField(default=dict)
    riasec_scores = models.JSONField(default=dict)
    values_scores = models.JSONField(default=dict)

    # Results
    recommended_stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    percentile = models.FloatField(null=True, blank=True)
    
    # Progress
    total_questions = models.PositiveIntegerField(default=0)
    questions_answered = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Test Session"
        verbose_name_plural = "Test Sessions"
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.test_type} for {self.student.name} ({self.status})"

    @property
    def progress_percentage(self):
        if self.total_questions > 0:
            return (self.questions_answered / self.total_questions) * 100
        return 0

    @property
    def is_expired(self):
        if self.status == 'IN_PROGRESS':
            # Expire sessions older than 3 hours
            return (timezone.now() - self.started_at).total_seconds() > 10800
        return False

class TestAnswer(models.Model):
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(AptitudeQuestion, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.SET_NULL, null=True, blank=True)
    is_correct = models.BooleanField(null=True)
    time_taken_seconds = models.PositiveIntegerField(null=True, blank=True)
    is_flagged = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Test Answer"
        verbose_name_plural = "Test Answers"
        unique_together = ('session', 'question')

    def __str__(self):
        return f"Ans for Q:{self.question_id} in Sess:{self.session_id}"
