from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Login(AbstractUser):
    is_student=models.BooleanField(default=False)
    name=models.CharField(max_length=100,null=True)
    email=models.EmailField(max_length=70,null=True,unique=True)



class College(models.Model):
    name=models.CharField(max_length=50,null=True)
    place=models.CharField(max_length=50,null=True)
    Type=models.CharField(max_length=50,null=True)
    Description=models.TextField(max_length=300,null=True) 
    cut_off_mark=models.PositiveBigIntegerField(null=True)
    user=models.OneToOneField(Login, on_delete=models.DO_NOTHING,null=True,related_name="college_profile")

    def __str__(self):
        return self.name

class Course(models.Model):
    College_name=models.ForeignKey(College, on_delete=models.CASCADE,null=True)
    Courses=models.CharField(max_length=50,null=True)

class Student(models.Model):
    name=models.CharField(max_length=50,null=True)
    place=models.CharField(max_length=50,null=True)
    phone=models.PositiveBigIntegerField(null=True) 
    age=models.PositiveIntegerField(null=True)
    Gender=models.CharField(max_length=50,null=True)
    email=models.EmailField(max_length=70,null=True,unique=True)
    qualification=models.CharField(max_length=200,null=True)
    user=models.OneToOneField(Login, on_delete=models.DO_NOTHING,related_name="student_profile")

    def __str__(self):
        return self.name

class Mark(models.Model):
    student_name=models.ForeignKey(Student, on_delete=models.CASCADE,null=True)
    Mark=models.PositiveBigIntegerField(null=True)

class Question(models.Model):
    question=models.CharField(max_length=300,null=True)

    def __str__(self):
        return self.question

class Answer(models.Model):
    question=models.ForeignKey(Question, on_delete=models.CASCADE,null=True)
    answer=models.CharField(max_length=30,null=True)

    TRUE_FALSE_CHOICES = [
        (True, 'True'),
        (False, 'False'),
    ]

    is_true=models.BooleanField(choices=TRUE_FALSE_CHOICES, default=False)

    def __str__(self):
        return self.answer

    


    





