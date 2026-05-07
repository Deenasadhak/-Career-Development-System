from django.db import models
from django.conf import settings

class CareerPath(models.Model):
    career_name = models.CharField(max_length=255)
    def __str__(self): return self.career_name
