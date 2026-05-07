import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Carrier_Counsil.settings')
django.setup()

from CarrierApp.models import Login
from core.models import StudentProfile
from core.models import District
from core.models import Stream

def seed_test_student():
    user, created = Login.objects.get_or_create(
        username='teststudent',
        email='teststudent@example.com',
        defaults={'role': 'STUDENT', 'is_student': True}
    )
    if created:
        user.set_password('pass123')
        user.save()

    district = District.objects.first()
    streams = Stream.objects.filter(is_active=True)[:2]

    profile, created = StudentProfile.objects.get_or_create(
        user=user,
        defaults={
            'name': 'Test Kumar',
            'phone': '9876543210',
            'gender': 'M',
            'community': 'GENERAL',
            'district': district,
            'plus_two_percentage': 88.5,
            'plus_two_marks': {'Mathematics': 92, 'Physics': 85, 'Chemistry': 80, 'English': 90},
            'keam_rank': 12500,
            'interest_keywords': ['coding', 'hardware', 'maths'],
            'max_fee_budget': 150000,
            'is_profile_complete': True,
            'profile_completion_pct': 100
        }
    )
    if not created:
        profile.plus_two_percentage = 88.5
        profile.plus_two_marks = {'Mathematics': 92, 'Physics': 85, 'Chemistry': 80, 'English': 90}
        profile.max_fee_budget = 150000
        profile.save()

    profile.interest_streams.set(streams)
    print(f"Created/Updated test student: {profile.user.email}")

if __name__ == "__main__":
    seed_test_student()
