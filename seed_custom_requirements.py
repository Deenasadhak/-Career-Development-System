import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Carrier_Counsil.settings")
django.setup()

from django.contrib.auth import get_user_model
from CarrierApp.models import Student as LegacyStudent, Mark, College as LegacyCollege
from core.models import StudentProfile
from core.models import AptitudeCategory, AptitudeQuestion, QuestionOption
from core.models import District, University
from core.models import Stream, Field, Discipline, Course
from core.models import College, CollegeCourse

User = get_user_model()

def seed_db():
    print("Seeding database...")
    
    # 1. Base geographies & streams
    ekm, _ = District.objects.get_or_create(name="Ernakulam")
    tsr, _ = District.objects.get_or_create(name="Thrissur")
    
    ktu, _ = University.objects.get_or_create(name="APJ Abdul Kalam Technological University")
    mgu, _ = University.objects.get_or_create(name="Mahatma Gandhi University")
    cu, _ = University.objects.get_or_create(name="Calicut University")
    
    science, _ = Stream.objects.update_or_create(slug="science", defaults={"name": "Science", "color_code": "#000"})
    commerce, _ = Stream.objects.update_or_create(slug="commerce", defaults={"name": "Commerce", "color_code": "#000"})
    arts, _ = Stream.objects.update_or_create(slug="arts", defaults={"name": "Arts", "color_code": "#000"})
    
    f_eng, _ = Field.objects.update_or_create(slug="engineering", defaults={"name": "Engineering", "stream": science})
    f_sci, _ = Field.objects.update_or_create(slug="pure-sciences", defaults={"name": "Pure Sciences", "stream": science})
    f_com, _ = Field.objects.update_or_create(slug="commerce-finance", defaults={"name": "Commerce & Finance", "stream": commerce})
    f_arts, _ = Field.objects.update_or_create(slug="humanities", defaults={"name": "Humanities", "stream": arts})
    
    d_csc, _ = Discipline.objects.update_or_create(slug="computer-science", defaults={"name": "Computer Science", "field": f_eng})
    d_ece, _ = Discipline.objects.update_or_create(slug="electronics", defaults={"name": "Electronics", "field": f_eng})
    d_psy, _ = Discipline.objects.update_or_create(slug="psychology", defaults={"name": "Psychology", "field": f_sci})
    d_com, _ = Discipline.objects.update_or_create(slug="bcom-general", defaults={"name": "B.Com General", "field": f_com})
    d_mgmt, _ = Discipline.objects.update_or_create(slug="management", defaults={"name": "Management", "field": f_com})
    d_eng, _ = Discipline.objects.update_or_create(slug="english", defaults={"name": "English", "field": f_arts})
    d_eco, _ = Discipline.objects.update_or_create(slug="economics", defaults={"name": "Economics", "field": f_arts})
    d_edu, _ = Discipline.objects.update_or_create(slug="education", defaults={"name": "Education", "field": f_arts})

    c_btech_cs, _ = Course.objects.update_or_create(slug="btech-cs", defaults={"name": "B.Tech Computer Science", "level": "UG", "duration_years": 4.0, "discipline": d_csc})
    c_btech_ec, _ = Course.objects.update_or_create(slug="btech-ec", defaults={"name": "B.Tech Electronics", "level": "UG", "duration_years": 4.0, "discipline": d_ece})
    c_bsc_cs, _ = Course.objects.update_or_create(slug="bsc-cs", defaults={"name": "B.Sc Computer Science", "level": "UG", "duration_years": 3.0, "discipline": d_csc})
    c_bsc_psy, _ = Course.objects.update_or_create(slug="bsc-psy", defaults={"name": "B.Sc Psychology", "level": "UG", "duration_years": 3.0, "discipline": d_psy})
    c_ba_eng, _ = Course.objects.update_or_create(slug="ba-eng", defaults={"name": "BA English", "level": "UG", "duration_years": 3.0, "discipline": d_eng})
    c_bcom, _ = Course.objects.update_or_create(slug="bcom", defaults={"name": "B.Com", "level": "UG", "duration_years": 3.0, "discipline": d_com})
    c_bba, _ = Course.objects.update_or_create(slug="bba", defaults={"name": "BBA", "level": "UG", "duration_years": 3.0, "discipline": d_mgmt})
    c_bca, _ = Course.objects.update_or_create(slug="bca", defaults={"name": "BCA", "level": "UG", "duration_years": 3.0, "discipline": d_csc})
    c_ba_eco, _ = Course.objects.update_or_create(slug="ba-eco", defaults={"name": "BA Economics", "level": "UG", "duration_years": 3.0, "discipline": d_eco})
    c_bed, _ = Course.objects.update_or_create(slug="bed", defaults={"name": "B.Ed", "level": "UG", "duration_years": 2.0, "discipline": d_edu})

    # 2. Colleges & College Users
    colleges_data = [
        {"name": "Model Engineering College", "u": "model_engineering", "p": "college123", "d": ekm, "t": "GOVT", "co": 420, "naac": "A+", "univ": ktu, "courses": [c_btech_cs, c_btech_ec]},
        {"name": "St. Teresa's College", "u": "st_teresas", "p": "college123", "d": ekm, "t": "AIDED", "co": 380, "naac": "A", "univ": mgu, "courses": [c_bsc_cs, c_bsc_psy, c_ba_eng]},
        {"name": "Sacred Heart College", "u": "sacred_heart", "p": "college123", "d": ekm, "t": "AIDED", "co": 350, "naac": "A", "univ": mgu, "courses": [c_bcom, c_bba, c_ba_eco]},
        {"name": "Rajagiri College", "u": "rajagiri", "p": "college123", "d": ekm, "t": "SF", "co": 400, "naac": "A+", "univ": ktu, "courses": [c_bca, c_btech_cs, c_bba]},
        {"name": "BCM College", "u": "bcm_college", "p": "college123", "d": tsr, "t": "AIDED", "co": 360, "naac": "B+", "univ": cu, "courses": [c_bcom, c_ba_eng, c_bed]},
    ]
    
    for cd in colleges_data:
        try:
            user = User.objects.get(username=cd["u"])
        except User.DoesNotExist:
            user = User.objects.create_user(username=cd["u"], password=cd["p"], email=f'{cd["u"]}@college.com', role='COLLEGE_ADMIN')
        user.set_password(cd["p"])
        user.save()
        
        # New model
        col, _ = College.objects.update_or_create(
            name=cd["name"],
            defaults={
                "slug": cd["u"],
                "college_code": cd["u"],
                "user": user,
                "college_type": cd["t"],
                "district": cd["d"],
                "naac_grade": cd["naac"],
                "university": cd["univ"]
            }
        )
        # Legacy model
        LegacyCollege.objects.update_or_create(
            user=user,
            defaults={
                "name": cd["name"],
                "place": cd["d"].name,
                "Type": cd["t"],
                "cut_off_mark": cd["co"]
            }
        )
        # Courses
        CollegeCourse.objects.filter(college=col).delete()
        for course_obj in cd["courses"]:
            CollegeCourse.objects.create(
                college=col,
                course=course_obj,
                total_intake=60,
                tuition_fee=50000,
                cutoff_general=cd["co"]
            )

    # 3. Student Account
    try:
        s_user = User.objects.get(username="test_student")
        s_user.set_password("student123")
        s_user.save()
    except User.DoesNotExist:
        s_user = User.objects.create_user(username="test_student", password="student123", email="test@student.com", role='STUDENT')
    
    # 3a. Legacy Student & Mark
    legacy_s, _ = LegacyStudent.objects.update_or_create(
        user=s_user,
        defaults={"name": "Test Student", "place": "Ernakulam", "email": "test@student.com", "qualification": "12th"}
    )
    Mark.objects.update_or_create(student_name=legacy_s, defaults={"Mark": 390})
    
    # 3b. Student Profile
    sp, _ = StudentProfile.objects.update_or_create(
        user=s_user,
        defaults={"name": "Test Student", "plus_two_percentage": 78, "plus_two_stream": "Science", "district": ekm}
    )

    # 4. Question Bank (30 questions, 6 per category)
    cats = ["Logical Reasoning", "Quantitative Aptitude", "Verbal Ability", "Technical/ICT", "Aesthetic/Creative"]
    AptitudeQuestion.objects.all().delete()
    
    for cat_name in cats:
        acat, _ = AptitudeCategory.objects.get_or_create(name=cat_name, defaults={"slug": cat_name.lower().replace(" ", "-"), "description": "Test"})
        for i in range(1, 7):
            q, _ = AptitudeQuestion.objects.update_or_create(
                question_text=f"Sample realistic question {i} for {cat_name} relevant for Kerala 12th grade?",
                defaults={
                    "category": acat,
                    "difficulty": 'M'
                }
            )
            for j in range(4):
                is_correct = (j == 0) # first option is correct
                QuestionOption.objects.update_or_create(
                    question=q,
                    option_text=f"Option {j+1} for Q{i}",
                    defaults={
                        "is_correct": is_correct
                    }
                )

    print("Seeding completed successfully.")

if __name__ == '__main__':
    seed_db()
