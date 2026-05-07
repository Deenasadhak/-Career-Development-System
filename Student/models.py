from django.db import models

# Create your models here.
class CourseBot(models.Model):
    stream = models.CharField(max_length=100)
    course = models.CharField(max_length=200)
    college = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.course} at {self.college}"
    
    class Meta:
        ordering = ['stream', 'course']