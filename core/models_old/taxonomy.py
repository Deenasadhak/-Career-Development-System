from django.db import models

class Stream(models.Model):
    """Top-level academic stream. e.g. Science & Technology"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.ImageField(upload_to='streams/', blank=True)
    color_code = models.CharField(max_length=7)       # hex e.g. #3B82F6
    description = models.TextField()
    suitable_for = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Stream"
        verbose_name_plural = "Streams"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Field(models.Model):
    """Second level. e.g. Engineering & Technology under Science"""
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE,
                               related_name='fields')
    name = models.CharField(max_length=150)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Field"
        verbose_name_plural = "Fields"
        ordering = ['order', 'name']
        unique_together = ('stream', 'slug')

    def __str__(self):
        return f"{self.name} ({self.stream.name})"

class Discipline(models.Model):
    """Third level. e.g. Computer Science & Engineering"""
    field = models.ForeignKey(Field, on_delete=models.CASCADE,
                              related_name='disciplines')
    name = models.CharField(max_length=150)
    slug = models.SlugField()
    overview = models.TextField()
    aptitude_tags = models.JSONField(default=list)
    # e.g. ["logical", "quantitative", "technical"]

    class Meta:
        verbose_name = "Discipline"
        verbose_name_plural = "Disciplines"
        ordering = ['name']
        unique_together = ('field', 'slug')

    def __str__(self):
        return f"{self.name} ({self.field.name})"

class Course(models.Model):
    """Fourth level. e.g. B.Tech, MBBS, B.Com"""
    LEVEL_CHOICES = [
        ('UG', 'Undergraduate'),
        ('PG', 'Postgraduate'),
        ('DIPLOMA', 'Diploma'),
        ('CERTIFICATE', 'Certificate'),
        ('PHD', 'Doctorate'),
        ('INTEGRATED', 'Integrated'),
    ]
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE,
                                   related_name='courses')
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    duration_years = models.FloatField()
    description = models.TextField()
    eligibility_description = models.TextField()
    min_percentage_required = models.FloatField(default=45.0)
    subjects_required = models.JSONField(default=list)
    # e.g. ["Physics", "Chemistry", "Mathematics"]
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ['name']
        unique_together = ('discipline', 'slug')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['level']),
        ]

    def __str__(self):
        return f"{self.name} ({self.level})"

class Specialization(models.Model):
    """Fifth level. e.g. AI & ML, Cybersecurity under B.Tech CSE"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               related_name='specializations')
    name = models.CharField(max_length=200)
    description = models.TextField()
    is_emerging = models.BooleanField(default=False)
    job_demand = models.CharField(
        max_length=10,
        choices=[('HIGH','High'),('MEDIUM','Medium'),('LOW','Low')]
    )

    class Meta:
        verbose_name = "Specialization"
        verbose_name_plural = "Specializations"
        ordering = ['name']
        unique_together = ('course', 'name')

    def __str__(self):
        return f"{self.name} in {self.course.name}"
