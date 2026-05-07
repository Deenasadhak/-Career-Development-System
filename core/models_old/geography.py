from django.db import models

class District(models.Model):
    REGION_CHOICES = [
        ('NORTH', 'North Kerala'),
        ('CENTRAL', 'Central Kerala'),
        ('SOUTH', 'South Kerala'),
    ]
    
    KERALA_DISTRICTS = [
        ('Thiruvananthapuram', 'Thiruvananthapuram'),
        ('Kollam', 'Kollam'),
        ('Pathanamthitta', 'Pathanamthitta'),
        ('Alappuzha', 'Alappuzha'),
        ('Kottayam', 'Kottayam'),
        ('Idukki', 'Idukki'),
        ('Ernakulam', 'Ernakulam'),
        ('Thrissur', 'Thrissur'),
        ('Palakkad', 'Palakkad'),
        ('Malappuram', 'Malappuram'),
        ('Kozhikode', 'Kozhikode'),
        ('Wayanad', 'Wayanad'),
        ('Kannur', 'Kannur'),
        ('Kasaragod', 'Kasaragod'),
    ]

    name = models.CharField(max_length=100, choices=KERALA_DISTRICTS, unique=True)
    region = models.CharField(max_length=20, choices=REGION_CHOICES)

    class Meta:
        verbose_name = "District"
        verbose_name_plural = "Districts"
        ordering = ['name']

    def __str__(self):
        return self.name

class University(models.Model):
    TYPE_CHOICES = [
        ('STATE', 'State University'),
        ('CENTRAL', 'Central University'),
        ('DEEMED', 'Deemed University'),
        ('PRIVATE', 'Private University'),
    ]

    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=50)
    university_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    website = models.URLField(blank=True)
    established_year = models.PositiveIntegerField(null=True)
    streams_covered = models.ManyToManyField('Stream', blank=True)

    class Meta:
        verbose_name = "University"
        verbose_name_plural = "Universities"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['short_name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.short_name})"
