from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Login(AbstractUser):
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('COLLEGE_ADMIN', 'College Admin'),
        ('COUNSELOR', 'Counselor'),
        ('SUPER_ADMIN', 'Super Admin'),
    ]
    LOGIN_METHODS = [
        ('EMAIL', 'Email'),
        ('PHONE', 'Phone'),
        ('GOOGLE', 'Google'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    login_method = models.CharField(max_length=10, choices=LOGIN_METHODS, default='EMAIL')
    
    is_student = models.BooleanField(default=False) # Keep for legacy compat
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=70, null=True, unique=True)




class Student(models.Model):
    DISTRICT_CHOICES = [
        ('Alappuzha', 'Alappuzha'), ('Ernakulam', 'Ernakulam'), ('Idukki', 'Idukki'),
        ('Kannur', 'Kannur'), ('Kasaragod', 'Kasaragod'), ('Kollam', 'Kollam'),
        ('Kottayam', 'Kottayam'), ('Kozhikode', 'Kozhikode'), ('Malappuram', 'Malappuram'),
        ('Palakkad', 'Palakkad'), ('Pathanamthitta', 'Pathanamthitta'),
        ('Thiruvananthapuram', 'Thiruvananthapuram'), ('Thrissur', 'Thrissur'),
        ('Wayanad', 'Wayanad'),
    ]
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    STREAM_CHOICES = [('Science', 'Science'), ('Commerce', 'Commerce'), ('Arts', 'Arts')]

    user = models.OneToOneField(Login, on_delete=models.CASCADE, related_name="student_profile")
    full_name = models.CharField(max_length=100, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True)
    district = models.CharField(max_length=50, choices=DISTRICT_CHOICES, null=True, blank=True)
    place = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=70, null=True, blank=True)
    
    sslc_percentage = models.FloatField(null=True, blank=True)
    stream_12th = models.CharField(max_length=50, choices=STREAM_CHOICES, null=True, blank=True)
    twelfth_percentage = models.FloatField(null=True, blank=True)
    interest_keywords = models.TextField(null=True, blank=True, help_text="Comma separated interests like Coding, Healthcare, Business")
    
    # Keeping age for compatibility if needed, but dob is preferred
    age = models.PositiveIntegerField(null=True, blank=True)
    qualification = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.full_name if self.full_name else self.user.username

    @property
    def completion_percentage(self):
        fields = ['full_name', 'dob', 'gender', 'district', 'place', 'phone', 'sslc_percentage', 'stream_12th', 'twelfth_percentage', 'interest_keywords']
        filled = 0
        for field in fields:
            val = getattr(self, field)
            if val is not None and val != '':
                filled += 1
        
        # Check if they have taken at least one test
        if self.marks.exists():
            filled += 1
            
        return int((filled / (len(fields) + 1)) * 100)

class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, related_name='marks')
    mark = models.IntegerField(null=True)
    ai_report = models.TextField(null=True, blank=True)
    dimensions_json = models.TextField(null=True, blank=True) # JSON string of dimension scores
    raw_responses = models.TextField(null=True, blank=True) # JSON string of [1, 2, 4...]
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    CATEGORY_CHOICES = [
        ('Aptitude', 'Aptitude'),
        ('English', 'English'),
        ('Mathematics', 'Mathematics'),
        ('Logic', 'Logical Reasoning'),
    ]
    question = models.CharField(max_length=500, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Aptitude')
    marks = models.IntegerField(default=1)

    def __str__(self):
        return f"[{self.category}] {self.question[:50]}"

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, related_name='options')
    answer = models.CharField(max_length=200, null=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer

    


    





