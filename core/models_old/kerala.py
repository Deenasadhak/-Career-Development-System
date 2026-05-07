from django.db import models
from django.db.models import JSONField
from core.models import Course
from core.models import Career

class CAPRound(models.Model):
    round_number = models.PositiveIntegerField()
    academic_year = models.CharField(max_length=9)
    registration_start = models.DateField(null=True, blank=True)
    registration_end = models.DateField(null=True, blank=True)
    allotment_date = models.DateField(null=True, blank=True)
    fee_payment_deadline = models.DateField(null=True, blank=True)
    reporting_start = models.DateField(null=True, blank=True)
    reporting_end = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [('round_number', 'academic_year')]
        ordering = ['academic_year', 'round_number']

    def __str__(self):
        return f"CAP Round {self.round_number} ({self.academic_year})"


class PSCDepartment(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PSCPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    department = models.ForeignKey(PSCDepartment, on_delete=models.CASCADE, related_name='posts')
    pay_scale = models.CharField(max_length=100)
    pay_grade = models.CharField(max_length=20, blank=True)
    description = models.TextField()
    eligibility_education = models.TextField()
    eligibility_age = models.CharField(max_length=100)
    qualifying_exam = models.CharField(max_length=200, blank=True)
    exam_syllabus_url = models.URLField(blank=True)
    notification_url = models.URLField(blank=True)
    related_careers = models.ManyToManyField(Career, blank=True, related_name='psc_posts')
    required_courses = models.ManyToManyField(Course, blank=True, related_name='psc_posts')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['department', 'title']
        unique_together = [('title', 'department')]

    def __str__(self):
        return f"{self.title} — {self.department.name}"


class GulfCountry(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    flag_emoji = models.CharField(max_length=5, blank=True)
    currency = models.CharField(max_length=10, blank=True)
    avg_salary_inr_lpa = models.FloatField(null=True, blank=True)
    kerala_workers_estimate = models.PositiveIntegerField(null=True, blank=True)
    popular_sectors = JSONField(default=list)
    visa_info = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class GulfCareerOpportunity(models.Model):
    DEMAND_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]

    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='gulf_opportunities')
    country = models.ForeignKey(GulfCountry, on_delete=models.CASCADE, related_name='career_opportunities')
    avg_salary_inr_lpa = models.FloatField()
    demand_level = models.CharField(max_length=20, choices=DEMAND_CHOICES)
    required_experience_years = models.PositiveIntegerField(default=0)
    required_certifications = JSONField(default=list)
    job_portals = JSONField(default=list)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [('career', 'country')]
        ordering = ['-demand_level', 'career']

    def __str__(self):
        return f"{self.career.title} in {self.country.name}"
