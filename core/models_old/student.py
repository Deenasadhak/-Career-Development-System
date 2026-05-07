from django.db import models
from django.conf import settings

# Using string references for related models to avoid circular imports
# Geography: core.District
# Taxonomy: core.Stream

class StudentProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('Prefer Not to Say', 'Prefer Not to Say'),
    ]
    COMMUNITY_CHOICES = [
        ('GENERAL', 'General'),
        ('OBC', 'OBC'),
        ('OBC_H', 'OBC Hindu'),
        ('SC', 'Scheduled Caste'),
        ('ST', 'Scheduled Tribe'),
        ('EWS', 'Economically Weaker Section'),
        ('LATIN_CATHOLIC', 'Latin Catholic'),
        ('OTHER_CHRISTIAN', 'Other Christian'),
        ('MUSLIM', 'Muslim'),
        ('EZHAVA', 'Ezhava'),
        ('NAIR', 'Nair'),
        ('VISWAKARMA', 'Viswakarma'),
    ]
    BOARD_CHOICES = [
        ('KERALA_STATE', 'Kerala State'),
        ('CBSE', 'CBSE'),
        ('ICSE', 'ICSE'),
        ('OTHER', 'Other Board'),
    ]
    PLUS_TWO_STREAM_CHOICES = [
        ('SCIENCE_PCM', 'Science (PCM)'),
        ('SCIENCE_PCB', 'Science (PCB)'),
        ('SCIENCE_PCMB', 'Science (PCMB)'),
        ('COMMERCE', 'Commerce'),
        ('HUMANITIES', 'Humanities'),
        ('VOCATIONAL', 'Vocational'),
    ]

    # User Link
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='core_profile')
    
    # Personal Info
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    district = models.ForeignKey('District', on_delete=models.SET_NULL, null=True, related_name='students')
    address = models.TextField(blank=True)
    pin_code = models.CharField(max_length=6, blank=True)
    
    community = models.CharField(max_length=20, choices=COMMUNITY_CHOICES, blank=True)
    is_pwd = models.BooleanField(default=False)
    pwd_type = models.CharField(max_length=100, blank=True)
    is_sports_quota = models.BooleanField(default=False)
    is_nri = models.BooleanField(default=False)
    annual_family_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # SSLC (10th) Details
    sslc_board = models.CharField(max_length=20, choices=BOARD_CHOICES, blank=True)
    sslc_school = models.CharField(max_length=255, blank=True)
    sslc_year = models.PositiveIntegerField(null=True, blank=True)
    sslc_percentage = models.FloatField(null=True, blank=True)
    sslc_marks = models.JSONField(default=dict, blank=True) # e.g. {"Maths": 95, "Science": 90}
    
    # Plus Two (12th) Details
    plus_two_board = models.CharField(max_length=20, choices=BOARD_CHOICES, blank=True)
    plus_two_school = models.CharField(max_length=255, blank=True)
    plus_two_year = models.PositiveIntegerField(null=True, blank=True)
    plus_two_stream = models.CharField(max_length=20, choices=PLUS_TWO_STREAM_CHOICES, blank=True)
    plus_two_percentage = models.FloatField(null=True, blank=True)
    plus_two_marks = models.JSONField(default=dict, blank=True) # e.g. {"Physics": 92, "Chemistry": 88}
    
    # Entrance Exam Scorces (Optional)
    keam_rank = models.PositiveIntegerField(null=True, blank=True)
    neet_score = models.PositiveIntegerField(null=True, blank=True)
    neet_rank = models.PositiveIntegerField(null=True, blank=True)
    jee_main_percentile = models.FloatField(null=True, blank=True)
    jee_advanced_rank = models.PositiveIntegerField(null=True, blank=True)
    clat_rank = models.PositiveIntegerField(null=True, blank=True)
    cat_percentile = models.FloatField(null=True, blank=True)
    kmat_rank = models.PositiveIntegerField(null=True, blank=True)
    cuet_score = models.FloatField(null=True, blank=True)
    other_exam_scores = models.JSONField(default=dict, blank=True)
    
    # Preferences & Psychometric
    preferred_stream = models.ForeignKey('Stream', on_delete=models.SET_NULL, null=True, blank=True)
    preferred_locations = models.ManyToManyField('District', blank=True, related_name='preferred_by_students')
    interest_streams = models.ManyToManyField('Stream', blank=True, related_name='interested_students')
    interest_keywords = models.JSONField(default=list, blank=True)
    career_goals = models.TextField(blank=True)
    max_fee_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Profile Completion
    profile_completion_pct = models.FloatField(default=0.0)
    is_profile_complete = models.BooleanField(default=False)
    
    # legacy fields (keeping for compat until migration)
    marks_10th = models.FloatField(null=True, blank=True)
    marks_12th = models.FloatField(null=True, blank=True)
    stream_12th = models.CharField(max_length=100, blank=True)
    subjects_12th = models.JSONField(default=list, blank=True)
    interests = models.JSONField(default=list, blank=True)
    skills = models.JSONField(default=list, blank=True)

    # Meta
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def calculate_completion(self):
        """Calculate profile completion percentage based on field presence."""
        required_fields = [
            'name', 'phone', 'gender', 'date_of_birth', 'district', 'address',
            'community', 'sslc_board', 'sslc_school', 'sslc_year', 'sslc_percentage',
            'plus_two_board', 'plus_two_school', 'plus_two_year', 'plus_two_stream', 'plus_two_percentage'
        ]
        
        filled_count = 0
        for field in required_fields:
            value = getattr(self, field)
            if value:
                filled_count += 1
        
        # Add bonus for optional fields
        optional_fields = ['photo', 'annual_family_income', 'preferred_stream', 'career_goals']
        for field in optional_fields:
            if getattr(self, field):
                filled_count += 0.5 # Half weight for optional
        
        total_weight = len(required_fields) + (len(optional_fields) * 0.5)
        self.profile_completion_pct = round((filled_count / total_weight) * 100, 2)
        
        # Consider complete if all required are filled
        all_required_filled = all([getattr(self, f) for f in required_fields])
        self.is_profile_complete = all_required_filled
        
        self.save()
        return self.profile_completion_pct
