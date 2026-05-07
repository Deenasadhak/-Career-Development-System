from django.db import models

class College(models.Model):
    user = models.OneToOneField('CarrierApp.Login', on_delete=models.SET_NULL, null=True, blank=True, related_name='college_profile')
    college_id = models.CharField(max_length=50, unique=True, null=True)
    name = models.CharField(max_length=200)
    district = models.CharField(max_length=50)
    city = models.CharField(max_length=100, blank=True)
    university = models.CharField(max_length=200, blank=True)
    college_type = models.CharField(max_length=100, blank=True)  
    address = models.TextField(blank=True)
    naac_grade = models.CharField(max_length=10, blank=True)
    naac_score = models.FloatField(null=True, blank=True)
    nirf_state_rank = models.IntegerField(null=True, blank=True)
    established_year = models.IntegerField(null=True, blank=True)
    total_seats = models.IntegerField(default=0)
    hostel_available = models.BooleanField(default=False)
    website = models.CharField(max_length=200, blank=True)
    contact_email = models.CharField(max_length=200, blank=True)
    contact_number = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['nirf_state_rank', 'naac_grade']
    
    def __str__(self):
        return f"{self.name} ({self.district})"

class Course(models.Model):
    course_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    stream = models.CharField(max_length=50)  # Science, Commerce, Arts
    discipline = models.CharField(max_length=100, blank=True)
    degree_type = models.CharField(max_length=50)  # UG, PG, Diploma
    duration_years = models.FloatField(default=3.0)
    min_percentage = models.IntegerField(default=45)
    eligible_streams = models.CharField(max_length=200, blank=True)
    kerala_demand_score = models.IntegerField(default=60)
    avg_salary_kerala = models.CharField(max_length=100, blank=True)
    top_job_roles = models.TextField(blank=True)
    psc_relevant = models.BooleanField(default=False)
    cap_applicable = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class CollegeCourse(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='college_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='college_courses')
    total_intake = models.IntegerField(default=0)
    govt_quota_seats = models.IntegerField(default=0)
    mgmt_quota_seats = models.IntegerField(default=0)
    cutoff_general = models.IntegerField(default=0)  # out of 600
    fee_per_year = models.CharField(max_length=100, default="0")
    academic_year = models.CharField(max_length=20, default="2024-2025")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('college', 'course')
    
    def __str__(self):
        return f"{self.college.name} — {self.course.name}"

class CareerPath(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='career_paths')
    career_path_name = models.CharField(max_length=200)
    top_job_roles = models.TextField()
    avg_salary_kerala = models.CharField(max_length=100)
    top_employers = models.TextField(blank=True)
    psc_exam_relevant = models.CharField(max_length=200, blank=True)
    gulf_opportunity = models.CharField(max_length=50, blank=True)
    further_studies = models.CharField(max_length=200, blank=True)
    demand_score = models.IntegerField(default=60)
    
    def __str__(self):
        return f"{self.course.name} → {self.career_path_name}"

class KeralaReference(models.Model):
    district = models.CharField(max_length=50, unique=True)
    region = models.CharField(max_length=50, blank=True)
    university_affiliation = models.CharField(max_length=500, blank=True)
    cap_nodal_center = models.CharField(max_length=500, blank=True)
    cap_helpline = models.CharField(max_length=100, blank=True)
    govt_quota_percent = models.IntegerField(default=75)
    mgmt_quota_percent = models.IntegerField(default=25)
    psc_exams = models.TextField(blank=True)
    
    def __str__(self):
        return self.district
