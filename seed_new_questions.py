import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Carrier_Counsil.settings')
django.setup()

from CarrierApp.models import Question, Answer

def seed_new_aptitude_test():
    # Clear old questions
    Question.objects.all().delete()
    Answer.objects.all().delete()

    questions_data = [
        {
            "q": "When you see a complex device, what is your first thought?",
            "options": [
                ("How do the parts work?", True),
                ("How much did it cost?", False),
                ("The design looks amazing", False),
                ("How does this help people?", False)
            ],
            "cat": "Investigative (Science)"
        },
        {
            "q": "In a high-stress situation, you usually:",
            "options": [
                ("Make a logical plan", True),
                ("Take charge of the group", False),
                ("Look for a creative escape", False),
                ("Try to calm everyone down", False)
            ],
            "cat": "Stress Tolerance (Medicine/Law)"
        },
        {
            "q": "If you were to write a blog, it would be about:",
            "options": [
                ("Latest Tech/Gadgets", True),
                ("Business/Startup tips", False),
                ("Poetry/Art reviews", False),
                ("Social issues/Kindness", False)
            ],
            "cat": "Personal Interest Mapping"
        },
        {
            "q": "How do you prefer to spend your weekends?",
            "options": [
                ("Solving puzzles or coding", True),
                ("Planning a small event", False),
                ("Sketching or playing music", False),
                ("Volunteering at a camp", False)
            ],
            "cat": "Artistic vs. Realistic"
        },
        {
            "q": "When faced with a 500-page book, you:",
            "options": [
                ("Read for technical facts", True),
                ("Skim for the main strategy", False),
                ("Get lost in the story", False),
                ("Think about the author's message", False)
            ],
            "cat": "Information Processing"
        },
        {
            "q": "You find a mistake in a document. You:",
            "options": [
                ("Feel a need to fix it", True),
                ("Delegate the fix", False),
                ("Think it adds character", False),
                ("Worry it might hurt someone's feelings", False)
            ],
            "cat": "Attention to Detail"
        },
        {
            "q": "Which environment sounds most appealing?",
            "options": [
                ("A quiet, high-tech lab", True),
                ("A fast-paced boardroom", False),
                ("A bright, open studio", False),
                ("A classroom or hospital", False)
            ],
            "cat": "Environmental Preference"
        },
        {
            "q": "Your friend is crying. Your natural instinct is:",
            "options": [
                ("Suggest a practical fix", False),
                ("Motivate them to move on", False),
                ("Write them a poem", False),
                ("Sit and listen patiently", True)
            ],
            "cat": "Social (Nursing/Social Work)"
        },
        {
            "q": "Do you prefer 'Knowing the Rules' or 'Making the Rules'?",
            "options": [
                ("Knowing (Safety)", False),
                ("Making (Leadership)", True),
                ("Breaking (Innovation)", False),
                ("Discussing (Fairness)", False)
            ],
            "cat": "Enterprising (Commerce)"
        },
        {
            "q": "When using an app, you focus most on:",
            "options": [
                ("Speed and efficiency", True),
                ("How much money it saves", False),
                ("The colors and layout", False),
                ("How easy it is for everyone", False)
            ],
            "cat": "Logic vs. Aesthetic"
        },
        {
            "q": "If you have to assemble furniture, you:",
            "options": [
                ("Follow instructions exactly", True),
                ("Build it and see what happens", False),
                ("Paint it a new color", False),
                ("Ask a friend to help", False)
            ],
            "cat": "Realistic (Technical)"
        },
        {
            "q": "Which word describes you best?",
            "options": [
                ("Logical", True),
                ("Ambitious", False),
                ("Imaginative", False),
                ("Compassionate", False)
            ],
            "cat": "Core Identity"
        },
        {
            "q": "You see a graph showing market trends. You feel:",
            "options": [
                ("Curious about the data", False),
                ("Excited by the profit", True),
                ("Bored by the visual", False),
                ("Concerned for the workers", False)
            ],
            "cat": "Commerce/Economics"
        },
        {
            "q": "When learning a new language, you enjoy:",
            "options": [
                ("The grammar rules", True),
                ("Using it for business", False),
                ("The sound and rhythm", False),
                ("Connecting with new cultures", False)
            ],
            "cat": "Analytical vs. Social"
        },
        {
            "q": "How do you feel about repetitive math problems?",
            "options": [
                ("Comforting and clear", True),
                ("A waste of time", False),
                ("I'd rather draw shapes", False),
                ("Better if done with a partner", False)
            ],
            "cat": "Conventional (Accountancy)"
        },
        {
            "q": "If you were an explorer, you'd search for:",
            "options": [
                ("New energy sources", True),
                ("New trade routes", False),
                ("Lost civilizations", False),
                ("Endangered species", False)
            ],
            "cat": "Core Values"
        },
        {
            "q": "Your ideal school project involves:",
            "options": [
                ("A working model", True),
                ("A business pitch", False),
                ("A short film", False),
                ("A community survey", False)
            ],
            "cat": "Stream Alignment"
        },
        {
            "q": "You prefer a job that offers:",
            "options": [
                ("Technical challenges", True),
                ("High financial rewards", False),
                ("Creative freedom", False),
                ("Emotional fulfillment", False)
            ],
            "cat": "Work Values"
        },
        {
            "q": "In a debate, you win by using:",
            "options": [
                ("Cold, hard facts", True),
                ("Confident persuasion", False),
                ("Vivid metaphors", False),
                ("Shared common values", False)
            ],
            "cat": "Communication Style"
        },
        {
            "q": "Why do you want a career?",
            "options": [
                ("To solve world problems", True),
                ("To lead and earn", False),
                ("To express myself", False),
                ("To help the needy", False)
            ],
            "cat": "Ultimate Goal"
        }
    ]

    for q_data in questions_data:
        question = Question.objects.create(
            question=q_data["q"],
            category=q_data["cat"][:50],
            marks=5 # 20 questions * 5 marks = 100 total
        )
        for opt_text, is_corr in q_data["options"]:
            Answer.objects.create(
                question=question,
                answer=opt_text,
                is_correct=is_corr
            )
    
    print(f"Successfully seeded {len(questions_data)} new questions.")

if __name__ == "__main__":
    seed_new_aptitude_test()
