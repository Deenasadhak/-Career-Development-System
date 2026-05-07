import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Carrier_Counsil.settings')
django.setup()

from core.models import College, CollegeCourse, CollegeCourseYearlyCutoff
from core.models import Discipline, Field, Stream, Course

def seed_courses():
    s, _ = Stream.objects.get_or_create(name='Science', slug='science', is_active=True)
    f, _ = Field.objects.get_or_create(name='Engineering', stream=s, slug='engineering')
    d1, _ = Discipline.objects.get_or_create(name='Computer Science Engineering', field=f, slug='computer-science-engineering')
    d2, _ = Discipline.objects.get_or_create(name='Mechanical Engineering', field=f, slug='mechanical-engineering')
    
    c1, _ = Course.objects.get_or_create(name='B.Tech CSE', discipline=d1, slug='btech-cse', level='UG', is_active=True, defaults={'duration_years': 4, 'min_percentage_required': 50.0})
    c2, _ = Course.objects.get_or_create(name='B.Tech Mech', discipline=d2, slug='btech-mech', level='UG', is_active=True, defaults={'duration_years': 4, 'min_percentage_required': 50.0})

    # Need a college
    college1, _ = College.objects.get_or_create(name='Govt Engg College', slug='gec', is_active=True, college_type='GOVT', defaults={'college_code': 'GEC01'})
    college2, _ = College.objects.get_or_create(name='Model Engg College', slug='mec', is_active=True, college_type='AIDED', defaults={'college_code': 'MEC01'})

    # Link courses to college
    cc1, _ = CollegeCourse.objects.get_or_create(college=college1, course=c1, is_active=True, defaults={'tuition_fee': 10000, 'cutoff_general': 80.0, 'total_intake': 60})
    cc2, _ = CollegeCourse.objects.get_or_create(college=college1, course=c2, is_active=True, defaults={'tuition_fee': 10000, 'cutoff_general': 70.0, 'total_intake': 60})
    cc3, _ = CollegeCourse.objects.get_or_create(college=college2, course=c1, is_active=True, defaults={'tuition_fee': 20000, 'cutoff_general': 85.0, 'total_intake': 60})
    cc4, _ = CollegeCourse.objects.get_or_create(college=college2, course=c2, is_active=True, defaults={'tuition_fee': 20000, 'cutoff_general': 75.0, 'total_intake': 60})

    print(f"Courses seeded: {CollegeCourse.objects.count()}")

if __name__ == "__main__":
    seed_courses()
