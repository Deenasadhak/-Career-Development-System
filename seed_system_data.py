import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Carrier_Counsil.settings')
django.setup()

from core.models import AptitudeCategory, AptitudeQuestion, TestAnswer
from core.models import University

def seed_data():
    print("Seeding Categorized Aptitude Data...")
    
    # 1. Categories
    categories = {
        "Logical Reasoning": "Ability to analyze patterns and reach logical conclusions.",
        "Quantitative Aptitude": "Mathematical skills and numerical problem-solving.",
        "Verbal Ability": "English language proficiency and comprehension.",
        "Technical Interest": "Interest and basic knowledge in science/tech fields.",
        "Arts & Humanities": "Creativity and interest in social sciences."
    }
    
    cat_objs = {}
    for name, desc in categories.items():
        cat, _ = AptitudeCategory.objects.get_or_create(name=name, defaults={'description': desc})
        cat_objs[name] = cat

    # 2. Questions & Answers
    questions_data = [
        # Logical Reasoning
        {
            "text": "If all cats are mammals and some mammals like fish, does it follow that some cats like fish?",
            "category": "Logical Reasoning",
            "difficulty": "medium",
            "answers": [
                ("Yes, definitely", False),
                ("No, not necessarily", True),
                ("Cats don't like fish", False),
                ("Mammals don't like fish", False)
            ]
        },
        {
            "text": "Identify the next number in the sequence: 2, 6, 12, 20, 30, ?",
            "category": "Logical Reasoning",
            "difficulty": "easy",
            "answers": [
                ("36", False),
                ("42", True),
                ("40", False),
                ("45", False)
            ]
        },
        # Quantitative Aptitude
        {
            "text": "What is the square root of 625?",
            "category": "Quantitative Aptitude",
            "difficulty": "easy",
            "answers": [
                ("15", False),
                ("25", True),
                ("35", False),
                ("45", False)
            ]
        },
        {
            "text": "If a car travels at 60 km/h, how far will it travel in 2.5 hours?",
            "category": "Quantitative Aptitude",
            "difficulty": "easy",
            "answers": [
                ("120 km", False),
                ("150 km", True),
                ("180 km", False),
                ("200 km", False)
            ]
        },
        # Technical Interest
        {
            "text": "Which of these is a programming language used for web development?",
            "category": "Technical Interest",
            "difficulty": "easy",
            "answers": [
                ("Python", True),
                ("Concrete", False),
                ("Aluminum", False),
                ("Hydrogen", False)
            ]
        },
        {
            "text": "What does CPU stand for?",
            "category": "Technical Interest",
            "difficulty": "easy",
            "answers": [
                ("Central Processing Unit", True),
                ("Computer Personal Unit", False),
                ("Control Process Unit", False),
                ("Central Peripheral Unit", False)
            ]
        }
    ]

    for q_data in questions_data:
        q, created = AptitudeQuestion.objects.get_or_create(
            question_text=q_data['text'],
            category=cat_objs[q_data['category']],
            defaults={'difficulty': q_data['difficulty']}
        )
        if created:
            for ans_text, is_correct in q_data['answers']:
                TestAnswer.objects.create(session=None, question=q, selected_option=None, is_correct=is_correct)

    # 3. Universities (Kerala)
    universities = [
        "University of Kerala",
        "Mahatma Gandhi University",
        "Calicut University",
        "Kannur University",
        "Cochin University of Science and Technology",
        "Kerala Agricultural University",
        "Kerala Veterinary and Animal Sciences University",
        "Kerala University of Health Sciences",
        "Kerala University of Fisheries and Ocean Studies",
        "APJ Abdul Kalam Technological University"
    ]
    for u_name in universities:
        University.objects.get_or_create(name=u_name)

    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed_data()
