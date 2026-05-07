from django.db import models
from django.conf import settings
from core.models import StudentProfile
from core.models import CollegeCourse
from core.models import TestSession

class StudentRecommendation(models.Model):
    ELIGIBLE = 'ELIGIBLE'
    BORDERLINE = 'BORDERLINE'
    INELIGIBLE = 'INELIGIBLE'
    
    ELIGIBILITY_CHOICES = [
        (ELIGIBLE, 'Eligible'),
        (BORDERLINE, 'Borderline'),
        (INELIGIBLE, 'Ineligible'),
    ]
    
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'
    
    CHANCE_CHOICES = [
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='recommendations')
    college_course = models.ForeignKey(CollegeCourse, on_delete=models.CASCADE)
    total_score = models.FloatField(default=0.0) # 0.0 to 100.0
    score_breakdown = models.JSONField(default=dict)
    # {"aptitude":82.0,"interest":75.0,"academic":90.0,"personality":68.0,"values":55.0}
    
    eligibility_status = models.CharField(max_length=20, choices=ELIGIBILITY_CHOICES)
    admission_chance = models.CharField(max_length=20, choices=CHANCE_CHOICES)
    
    cutoff_gap = models.FloatField(help_text="positive = student above cutoff, negative = below")
    why_recommended = models.TextField()
    action_steps = models.JSONField(default=list)
    # ["Apply before March 15", "Prepare for KEAM", ...]
    
    is_shortlisted = models.BooleanField(default=False)
    shortlisted_at = models.DateTimeField(null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    based_on_session = models.ForeignKey(TestSession, on_delete=models.SET_NULL, null=True, blank=True)
    rank = models.PositiveIntegerField(default=0) # rank within this student's recommendation list
    
    class Meta:
        ordering = ['-total_score']
        indexes = [
            models.Index(fields=['student', 'is_shortlisted']),
            models.Index(fields=['student', 'total_score']),
        ]
        verbose_name = "Student Recommendation"
        verbose_name_plural = "Student Recommendations"

    def __str__(self):
        return f"Rec for {self.student.name}: {self.college_course}"

class ShortlistNote(models.Model):
    recommendation = models.ForeignKey(StudentRecommendation, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Shortlist Note"
        verbose_name_plural = "Shortlist Notes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Note on {self.recommendation}"
