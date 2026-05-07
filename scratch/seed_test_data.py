# scratch/seed_test_data.py
import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Carrier_Counsil.settings')
django.setup()

from django.contrib.auth import get_user_model
from CarrierApp.models import Student, Mark, Login

User = Login # CarrierApp.models.Login is the auth model

def seed():
    # 1. Create a test user if not exists
    user, created = User.objects.get_or_create(
        username='teststudent',
        defaults={'role': 'STUDENT'}
    )
    if created:
        user.set_password('password123')
        user.save()

    # 2. Create student profile
    student, created = Student.objects.update_or_create(
        user=user,
        defaults={
            'full_name': 'Anand K. P.',
            'district': 'Ernakulam',
            'stream_12th': 'Science',
            'twelfth_percentage': 85.5,
            'age': 18,
            'email': 'anand@example.com'
        }
    )

    # 3. Create a test aptitude mark
    Mark.objects.update_or_create(
        student=student,
        defaults={'mark': 510} # out of 600
    )

    print("Test student 'teststudent' seeded with mark 510/600.")

if __name__ == '__main__':
    seed()
