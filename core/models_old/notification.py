from django.db import models
from django.conf import settings
from django.utils import timezone

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('ADMISSION_DEADLINE', 'Admission Deadline'),
        ('EXAM_DATE', 'Exam Date Reminder'),
        ('CUTOFF_RELEASED', 'Cutoff Released'),
        ('SCHOLARSHIP_DEADLINE', 'Scholarship Deadline'),
        ('RECOMMENDATION_READY', 'Your Recommendations Ready'),
        ('PROFILE_INCOMPLETE', 'Complete Your Profile'),
        ('NEW_COLLEGE', 'New College Added'),
        ('CAP_ROUND_OPENING', 'CAP Round Opening Soon'),
        ('TEST_REMINDER', 'Take Your Aptitude Test'),
        ('SHORTLIST_REMINDER', 'Review Your Shortlist'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', 'created_at']),
            models.Index(fields=['notification_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.get_notification_type_display()} -> {self.recipient.email}"

    @property
    def is_expired(self):
        if self.expires_at:
            return self.expires_at < timezone.now()
        return False

    @property
    def is_visible(self):
        return not self.is_expired

class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    admission_deadline = models.BooleanField(default=True)
    exam_date = models.BooleanField(default=True)
    cutoff_released = models.BooleanField(default=True)
    scholarship_deadline = models.BooleanField(default=True)
    recommendation_ready = models.BooleanField(default=True)
    profile_incomplete = models.BooleanField(default=True)
    new_college = models.BooleanField(default=False)
    cap_round_opening = models.BooleanField(default=True)
    test_reminder = models.BooleanField(default=True)
    shortlist_reminder = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Notification Preferences"

    def __str__(self):
        return f"Preferences for {self.user.email}"
