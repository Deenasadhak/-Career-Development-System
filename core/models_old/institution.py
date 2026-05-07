from django.conf import settings
from django.db import models
from .geography import District, University
from .taxonomy import Course, Specialization

class College(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='college_profile_core')
    COLLEGE_TYPE_CHOICES = [
        ('GOVT', 'Government'),
        ('AIDED', 'Government Aided'),
        ('SF', 'Self Financing'),
        ('AUTONOMOUS', 'Autonomous'),
        ('DEEMED', 'Deemed'),
        ('CENTRAL', 'Central Institution'),
    ]
    NAAC_CHOICES = [
        ('A++', 'A++'), ('A+', 'A+'), ('A', 'A'),
        ('B++', 'B++'), ('B+', 'B+'), ('B', 'B'),
        ('C', 'C'), ('PENDING', 'Awaiting'), ('NA', 'Not Accredited'),
    ]

    # Identity
    name = models.CharField(max_length=300)
    short_name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True)
    college_code = models.CharField(max_length=20, unique=True, blank=True)

    admin_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name='administered_college',
        on_delete=models.SET_NULL,
    )

    # Classification
    college_type = models.CharField(max_length=20, choices=COLLEGE_TYPE_CHOICES)
    university = models.ForeignKey(University, on_delete=models.SET_NULL,
                                   null=True, related_name='colleges')
    district = models.ForeignKey(District, on_delete=models.SET_NULL,
                                 null=True, related_name='colleges')
    is_minority = models.BooleanField(default=False)
    minority_type = models.CharField(
        max_length=20,
        choices=[('LINGUISTIC', 'Linguistic'), ('RELIGIOUS', 'Religious'), ('NA', 'N/A')],
        default='NA'
    )
    is_women_only = models.BooleanField(default=False)

    # Accreditation & Ranking
    naac_grade = models.CharField(max_length=10, choices=NAAC_CHOICES, default='NA')
    nirf_rank = models.PositiveIntegerField(null=True, blank=True)
    nba_accredited = models.BooleanField(default=False)
    established_year = models.PositiveIntegerField(null=True, blank=True)

    # Location
    address = models.TextField()
    taluk = models.CharField(max_length=100, blank=True)
    pin_code = models.CharField(max_length=6, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6,
                                   null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,
                                    null=True, blank=True)
    nearest_railway_station = models.CharField(max_length=100, blank=True)
    nearest_railway_km = models.FloatField(null=True, blank=True)
    nearest_bus_stand = models.CharField(max_length=100, blank=True)
    nearest_bus_km = models.FloatField(null=True, blank=True)

    # Contact
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    # Facilities
    has_hostel_boys = models.BooleanField(default=False)
    has_hostel_girls = models.BooleanField(default=False)
    has_transport = models.BooleanField(default=False)
    has_wifi = models.BooleanField(default=False)
    has_library = models.BooleanField(default=False)
    has_sports = models.BooleanField(default=False)
    has_canteen = models.BooleanField(default=False)
    has_medical = models.BooleanField(default=False)
    has_placement_cell = models.BooleanField(default=False)
    has_nss = models.BooleanField(default=False)
    has_ncc = models.BooleanField(default=False)

    # Stats
    total_student_strength = models.PositiveIntegerField(null=True, blank=True)
    campus_area_acres = models.FloatField(null=True, blank=True)

    # Meta
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "College"
        verbose_name_plural = "Colleges"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['college_type']),
        ]

    # Backward compatibility properties
    @property
    def place(self):
        return self.district.name if self.district else ''

    @property
    def Type(self):
        return self.get_college_type_display()

    def __str__(self):
        return self.name

class CollegeCourse(models.Model):
    MEDIUM_CHOICES = [
        ('EN', 'English'), ('ML', 'Malayalam'), ('BI', 'Bilingual')
    ]
    COURSE_MODE_CHOICES = [
        ('REGULAR', 'Regular'), ('DISTANCE', 'Distance'),
        ('ONLINE', 'Online'), ('PART_TIME', 'Part Time')
    ]
    ADMISSION_MODE_CHOICES = [
        ('CAP', 'Centralized Allotment (CAP)'),
        ('MANAGEMENT', 'Management Quota'),
        ('NRI', 'NRI Quota'),
        ('DIRECT', 'Direct Admission'),
    ]

    college = models.ForeignKey(College, on_delete=models.CASCADE,
                                related_name='college_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               related_name='college_courses')
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL,
                                       null=True, blank=True)

    # Intake
    total_intake = models.PositiveIntegerField()
    govt_quota_seats = models.PositiveIntegerField(default=0)
    management_quota_seats = models.PositiveIntegerField(default=0)
    nri_quota_seats = models.PositiveIntegerField(default=0)

    # Fees (annual, in INR)
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2)
    hostel_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exam_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    caution_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Cutoffs
    cutoff_general = models.FloatField(null=True, blank=True)
    cutoff_sc = models.FloatField(null=True, blank=True)
    cutoff_st = models.FloatField(null=True, blank=True)
    cutoff_obc = models.FloatField(null=True, blank=True)
    cutoff_ews = models.FloatField(null=True, blank=True)

    # Course delivery
    medium = models.CharField(max_length=2, choices=MEDIUM_CHOICES, default='EN')
    course_mode = models.CharField(max_length=20, choices=COURSE_MODE_CHOICES,
                                   default='REGULAR')
    admission_mode = models.CharField(max_length=20, choices=ADMISSION_MODE_CHOICES,
                                      default='CAP')
    lateral_entry_available = models.BooleanField(default=False)

    # Placement data
    placement_percentage = models.FloatField(null=True, blank=True)
    avg_package_lpa = models.FloatField(null=True, blank=True)
    highest_package_lpa = models.FloatField(null=True, blank=True)
    top_recruiters = models.JSONField(default=list)

    # Meta
    is_active = models.BooleanField(default=True)
    academic_year = models.CharField(max_length=9, default='2024-2025')

    class Meta:
        verbose_name = "College Course"
        verbose_name_plural = "College Courses"
        unique_together = [('college', 'course', 'specialization', 'academic_year')]
        indexes = [
            models.Index(fields=['college', 'course']),
            models.Index(fields=['cutoff_general']),
        ]

    # Backward compat
    @property
    def cut_off_mark(self):
        return self.cutoff_general

    @property
    def Courses(self):
        return self.course.name

    def __str__(self):
        name = self.course.name
        if self.specialization:
            name += f" ({self.specialization.name})"
        return f"{name} at {self.college.name}"

class CollegeCourseYearlyCutoff(models.Model):
    """Store 5-year cutoff history per category"""
    college_course = models.ForeignKey(CollegeCourse, on_delete=models.CASCADE,
                                       related_name='yearly_cutoffs')
    year = models.PositiveIntegerField()
    cutoff_general = models.FloatField(null=True, blank=True)
    cutoff_sc = models.FloatField(null=True, blank=True)
    cutoff_st = models.FloatField(null=True, blank=True)
    cutoff_obc = models.FloatField(null=True, blank=True)
    cutoff_ews = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Yearly Cutoff"
        verbose_name_plural = "Yearly Cutoffs"
        unique_together = [('college_course', 'year')]
        ordering = ['-year']

    def __str__(self):
        return f"{self.year} Cutoff for {self.college_course}"
