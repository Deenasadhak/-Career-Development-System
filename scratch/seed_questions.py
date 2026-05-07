import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Carrier_Counsil.settings')
django.setup()

from CarrierApp.models import Question, Answer

questions_data = [
    # Aptitude
    ("Which of the following is a prime number?", "Aptitude", [("15", False), ("21", False), ("17", True), ("25", False)]),
    ("A train 100m long passes a bridge in 10s. If the train is moving at 72km/hr, what is the length of the bridge?", "Aptitude", [("100m", True), ("150m", False), ("200m", False), ("50m", False)]),
    ("The average of first five multiples of 3 is:", "Aptitude", [("3", False), ("9", True), ("12", False), ("15", False)]),
    ("If 20% of a number is 120, then 120% of that number will be:", "Aptitude", [("20", False), ("120", False), ("480", False), ("720", True)]),
    ("A person crosses a 600 m long street in 5 minutes. What is his speed in km/hr?", "Aptitude", [("3.6", False), ("7.2", True), ("8.4", False), ("10", False)]),
    ("If the cost price is 25% of selling price, then what is the profit percent?", "Aptitude", [("150%", False), ("200%", False), ("300%", True), ("350%", False)]),
    ("A and B can do a work in 12 days. B and C in 15 days, C and A in 20 days. If A, B and C work together, they will complete the work in:", "Aptitude", [("5 days", False), ("10 days", True), ("12 days", False), ("15 days", False)]),
    
    # English
    ("Choose the correct synonym for 'Diligent'.", "English", [("Lazy", False), ("Hardworking", True), ("Shy", False), ("Clever", False)]),
    ("Identify the correctly spelled word.", "English", [("Accommodate", True), ("Acomodate", False), ("Accomodate", False), ("Acommodate", False)]),
    ("Fill in the blank: Neither of the two candidates ____ selected.", "English", [("are", False), ("were", False), ("was", True), ("have", False)]),
    ("What is the antonym of 'Optimist'?", "English", [("Idealist", False), ("Pessimist", True), ("Realist", False), ("Activist", False)]),
    ("Complete the idiom: 'Break a ____'", "English", [("hand", False), ("leg", True), ("bone", False), ("heart", False)]),
    ("Choose the correctly punctuated sentence.", "English", [("Its a beautiful day.", False), ("It's a beautiful day.", True), ("Its' a beautiful day.", False), ("It is a beautiful day?", False)]),
    ("What is the meaning of 'In a nutshell'?", "English", [("Briefly", True), ("In a box", False), ("Hard to crack", False), ("Confused", False)]),
    
    # Mathematics
    ("What is the value of Pi (approximately)?", "Mathematics", [("3.12", False), ("3.14", True), ("3.16", False), ("3.18", False)]),
    ("The sum of angles in a triangle is:", "Mathematics", [("90", False), ("180", True), ("270", False), ("360", False)]),
    ("If x + 5 = 12, then x is:", "Mathematics", [("5", False), ("7", True), ("17", False), ("12", False)]),
    ("The square root of 625 is:", "Mathematics", [("15", False), ("25", True), ("35", False), ("45", False)]),
    ("A triangle with all three sides equal is called:", "Mathematics", [("Isosceles", False), ("Scalene", False), ("Equilateral", True), ("Right-angled", False)]),
    ("The value of log10(1000) is:", "Mathematics", [("1", False), ("2", False), ("3", True), ("4", False)]),
    ("The volume of a sphere is (4/3) * Pi * r^k. What is k?", "Mathematics", [("1", False), ("2", False), ("3", True), ("4", False)]),
    ("What is the derivative of x^2?", "Mathematics", [("x", False), ("2x", True), ("2", False), ("x^2", False)]),
    
    # Logical Reasoning
    ("Find the missing number in the series: 2, 6, 12, 20, 30, ?", "Logical Reasoning", [("36", False), ("40", False), ("42", True), ("48", False)]),
    ("If COBALT is coded as 315211220, then GOLD is coded as:", "Logical Reasoning", [("715124", True), ("715123", False), ("816134", False), ("716124", False)]),
    ("Point out to a photograph, a man says, 'I have no brother, and that man's father is my father's son.' Who is in the photograph?", "Logical Reasoning", [("His son", True), ("His father", False), ("Himself", False), ("His nephew", False)]),
    ("Light : Sun :: Heat : ?", "Logical Reasoning", [("Electricity", False), ("Moon", False), ("Fire", True), ("Stars", False)]),
    ("A is the mother of B and C. If D is the husband of C. What is A to D?", "Logical Reasoning", [("Mother", False), ("Sister", False), ("Mother-in-law", True), ("Aunt", False)]),
    ("Which word does not belong with the others?", "Logical Reasoning", [("Leopard", False), ("Cougar", False), ("Elephant", True), ("Lion", False)]),
    ("If red is called blue, blue is called white, white is called black, what is the color of milk?", "Logical Reasoning", [("White", False), ("Black", True), ("Blue", False), ("Red", False)]),
    ("SCD, TEF, UGH, ____, WKL", "Logical Reasoning", [("CMN", False), ("UJI", False), ("VIJ", True), ("IJT", False)]),
]

def seed():
    print(f"Seeding {len(questions_data)} questions...")
    for q_text, cat, options in questions_data:
        q = Question.objects.create(question=q_text, category=cat, marks=5) # 30 * 5 = 150 points
        for opt_text, correct in options:
            Answer.objects.create(question=q, answer=opt_text, is_correct=correct)
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
