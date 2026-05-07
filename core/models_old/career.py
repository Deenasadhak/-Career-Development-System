from django.db import models
from django.db.models import JSONField
from core.models import Course, Stream
import django.utils.timezone

class CareerCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Career Categories"

    def __str__(self):
        return self.name

class Career(models.Model):
    WORK_ENV_CHOICES = [
        ('OFFICE', 'Office'),
        ('FIELD', 'Field'),
        ('REMOTE', 'Remote'),
        ('MIXED', 'Mixed'),
        ('OUTDOOR', 'Outdoor'),
        ('CLINICAL', 'Clinical'),
    ]
    
    DEMAND_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(CareerCategory, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    day_in_life = models.TextField()
    work_environment = models.CharField(max_length=20, choices=WORK_ENV_CHOICES)
    
    riasec_primary = models.CharField(max_length=1, blank=True)
    riasec_secondary = models.CharField(max_length=1, blank=True)

    salary_kerala_min = models.FloatField()
    salary_kerala_max = models.FloatField()
    salary_india_avg = models.FloatField()
    salary_abroad_avg = models.FloatField(null=True, blank=True)

    job_demand = models.CharField(max_length=20, choices=DEMAND_CHOICES)
    growth_rate_pct = models.FloatField()
    kerala_job_market_notes = models.TextField()
    gulf_opportunity = models.BooleanField(default=False)
    gulf_notes = models.TextField(blank=True)

    technical_skills = JSONField(default=list)
    soft_skills = JSONField(default=list)

    entry_roles = JSONField(default=list)
    mid_roles = JSONField(default=list)
    senior_roles = JSONField(default=list)
    progression_timeline = JSONField(default=dict)

    top_employers_kerala = JSONField(default=list)
    top_employers_india = JSONField(default=list)
    top_employers_abroad = JSONField(default=list)

    who_should_choose = models.TextField()
    who_should_avoid = models.TextField()
    advantages = models.TextField()
    challenges = models.TextField()
    minimum_qualification = models.CharField(max_length=200)

    qualifying_courses = models.ManyToManyField(Course, related_name='career_outcomes', blank=True)
    related_careers = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='related_to')

    is_ayurveda_related = models.BooleanField(default=False)
    is_tourism_related = models.BooleanField(default=False)
    is_psc_available = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['category', 'job_demand', 'is_active']),
            models.Index(fields=['gulf_opportunity']),
            models.Index(fields=['riasec_primary']),
        ]

    def __str__(self):
        return self.title

    @property
    def salary_range_kerala(self):
        def format_lpa(value):
            if value >= 100:
                return f"₹{value/100:.1f}Cr"
            return f"₹{value:g}L"
        return f"{format_lpa(self.salary_kerala_min)} – {format_lpa(self.salary_kerala_max)} per annum"

    @property
    def is_high_demand(self):
        return self.job_demand == 'HIGH'


class EntranceExam(models.Model):
    LEVEL_CHOICES = [
        ('STATE', 'State'),
        ('NATIONAL', 'National'),
        ('UNIVERSITY', 'University'),
    ]
    
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=30, unique=True)
    conducting_body = models.CharField(max_length=200)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    description = models.TextField()
    eligibility = models.TextField()
    exam_pattern = JSONField(default=dict)
    
    official_website = models.URLField(blank=True)
    notification_month = models.CharField(max_length=20, blank=True)
    exam_month = models.CharField(max_length=20, blank=True)
    result_month = models.CharField(max_length=20, blank=True)
    
    is_kerala_specific = models.BooleanField(default=False)
    courses_unlocked = models.ManyToManyField(Course, related_name='unlocked_by_exams', blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['level', 'name']

    def __str__(self):
        return f"{self.short_name} - {self.name}"


class Scholarship(models.Model):
    TYPE_CHOICES = [
        ('MERIT', 'Merit'),
        ('NEED', 'Need'),
        ('COMMUNITY', 'Community'),
        ('SPORTS', 'Sports'),
        ('GIRL_CHILD', 'Girl Child'),
        ('PWD', 'PWD'),
        ('GOVT', 'Government'),
    ]

    name = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    offering_organization = models.CharField(max_length=200)
    scholarship_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()

    eligible_communities = JSONField(default=list)
    eligible_streams = models.ManyToManyField(Stream, blank=True)
    eligible_courses = models.ManyToManyField(Course, blank=True)
    eligible_plus_two_streams = JSONField(default=list)
    
    income_ceiling_annual = models.PositiveIntegerField(null=True, blank=True)
    min_percentage_required = models.FloatField(default=0.0)
    is_pwd_only = models.BooleanField(default=False)
    is_girl_only = models.BooleanField(default=False)

    amount_per_year = models.PositiveIntegerField()
    is_renewable = models.BooleanField(default=True)
    renewal_conditions = models.TextField(blank=True)
    application_portal = models.URLField(blank=True)
    application_deadline_month = models.CharField(max_length=20, blank=True)
    documents_required = JSONField(default=list)

    is_kerala_specific = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scholarship_type', 'name']

    def __str__(self):
        return self.name

    def is_eligible_for(self, student_profile) -> bool:
        if self.eligible_communities:
            if not student_profile.community or student_profile.community not in self.eligible_communities:
                return False
                
        if self.income_ceiling_annual is not None:
            if student_profile.annual_family_income is None or student_profile.annual_family_income > self.income_ceiling_annual:
                return False
                
        if self.min_percentage_required > 0:
            if student_profile.plus_two_percentage is None or student_profile.plus_two_percentage < self.min_percentage_required:
                return False
                
        if self.is_pwd_only:
            if not student_profile.is_pwd:
                return False
                
        if self.is_girl_only:
            if student_profile.gender != 'F':
                return False
                
        if self.eligible_plus_two_streams:
            if not student_profile.plus_two_stream or student_profile.plus_two_stream not in self.eligible_plus_two_streams:
                return False
                
        # Optional: check streams/courses if needed, but not specified in prompt logic checklist
        return True
