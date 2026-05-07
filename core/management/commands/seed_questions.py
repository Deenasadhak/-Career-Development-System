from django.core.management.base import BaseCommand
from core.models import AptitudeCategory, AptitudeQuestion, QuestionOption
from core.models import Stream
from django.db import transaction

class Command(BaseCommand):
    help = "Seeds the database with 120+ aptitude questions across 8 categories."

    def handle(self, *args, **options):
        self.stdout.write("Seeding Aptitude Categories and Questions...")
        
        # 1. Categories
        categories_data = [
            {'code': 'LOGICAL', 'name': 'Logical Reasoning', 'order': 1, 'desc': 'Number series, patterns, and syllogisms.'},
            {'code': 'QUANTITATIVE', 'name': 'Quantitative Aptitude', 'order': 2, 'desc': 'Mathematical and numerical problem solving.'},
            {'code': 'VERBAL', 'name': 'Verbal Ability', 'order': 3, 'desc': 'Grammar, vocabulary, and reading comprehension.'},
            {'code': 'TECHNICAL', 'name': 'Technical/ICT', 'order': 4, 'desc': 'Computer science, logic, and technical awareness.'},
            {'code': 'ARTS', 'name': 'Aesthetic/Creative', 'order': 5, 'desc': 'Visual reasoning, design, and creative thinking.'},
            {'code': 'PERSONALITY', 'name': 'Personality (Big Five)', 'order': 6, 'desc': 'Big Five personality trait assessment.'},
            {'code': 'INTEREST', 'name': 'Interest (RIASEC)', 'order': 7, 'desc': 'Holland Code career interest inventory.'},
            {'code': 'VALUES', 'name': 'Work Values', 'order': 8, 'desc': 'Assessment of workplace priorities and values.'},
        ]

        categories = {}
        for cat_item in categories_data:
            cat, created = AptitudeCategory.objects.get_or_create(
                code=cat_item['code'],
                defaults={'name': cat_item['name'], 'order': cat_item['order'], 'description': cat_item['desc']}
            )
            categories[cat.code] = cat

        # 2. Streams for mapping
        sci_tech = Stream.objects.filter(slug='science-technology').first()
        eng = Stream.objects.filter(slug='engineering').first()
        med = Stream.objects.filter(slug='medical-sciences').first()
        comm = Stream.objects.filter(slug='commerce-management').first()
        arts = Stream.objects.filter(slug='arts-humanities').first()
        law = Stream.objects.filter(slug='law').first()

        if sci_tech: categories['TECHNICAL'].maps_to_streams.add(sci_tech)
        if eng: categories['LOGICAL'].maps_to_streams.add(eng)
        if med: categories['LOGICAL'].maps_to_streams.add(med)
        if comm: categories['QUANTITATIVE'].maps_to_streams.add(comm)
        if arts: categories['ARTS'].maps_to_streams.add(arts)

        # 3. Questions (15 per category = 120)
        
        with transaction.atomic():
            # --- LOGICAL ---
            self.seed_logical(categories['LOGICAL'])
            # --- QUANTITATIVE ---
            self.seed_quantitative(categories['QUANTITATIVE'])
            # --- VERBAL ---
            self.seed_verbal(categories['VERBAL'])
            # --- TECHNICAL ---
            self.seed_technical(categories['TECHNICAL'])
            # --- ARTS ---
            self.seed_arts(categories['ARTS'])
            # --- PERSONALITY ---
            self.seed_personality(categories['PERSONALITY'])
            # --- INTEREST ---
            self.seed_interest(categories['INTEREST'])
            # --- VALUES ---
            self.seed_values(categories['VALUES'])

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {AptitudeQuestion.objects.count()} questions across 8 categories."))

    def add_mcq(self, category, text, options, difficulty='M', tag='', explanation=''):
        q, created = AptitudeQuestion.objects.get_or_create(
            category=category,
            question_text=text,
            defaults={'difficulty': difficulty, 'topic_tag': tag, 'explanation': explanation, 'question_type': 'MCQ'}
        )
        if created:
            for i, opt in enumerate(options):
                QuestionOption.objects.create(
                    question=q,
                    option_text=opt['text'],
                    is_correct=opt.get('is_correct', False),
                    riasec_code=opt.get('riasec', ''),
                    order=i
                )

    def add_likert(self, category, text, tag, difficulty='E'):
        q, created = AptitudeQuestion.objects.get_or_create(
            category=category,
            question_text=text,
            defaults={'difficulty': difficulty, 'topic_tag': tag, 'question_type': 'LIKERT'}
        )
        if created:
            options = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
            for i, opt in enumerate(options):
                QuestionOption.objects.create(question=q, option_text=opt, order=i+1)

    def seed_logical(self, cat):
        sq = [
            ("What comes next in the series: 2, 6, 12, 20, 30, ...?", [{"text": "40"}, {"text": "42", "is_correct": True}, {"text": "44"}, {"text": "46"}], 'E', 'number_series'),
            ("If BOOK is coded as 43, what is READ coded as?", [{"text": "28", "is_correct": True}, {"text": "30"}, {"text": "32"}, {"text": "25"}], 'M', 'coding_decoding'),
            ("Complete the analogy: Ocean : Water :: Glacier : ?", [{"text": "Mountain"}, {"text": "Ice", "is_correct": True}, {"text": "Cold"}, {"text": "River"}], 'E', 'analogy'),
            ("Pointing to a man, a lady said, 'He is the son of my husband's father'. Who is the man?", [{"text": "Father-in-law"}, {"text": "Brother-in-law", "is_correct": True}, {"text": "Nephew"}, {"text": "Son"}], 'M', 'blood_relations'),
            ("Find the odd one out: 64, 125, 216, 343, 512, 721.", [{"text": "125"}, {"text": "343"}, {"text": "721", "is_correct": True}, {"text": "216"}], 'H', 'odd_one_out'),
            ("Statement: All cats are dogs. All dogs are birds. Conclusion: All cats are birds?", [{"text": "True", "is_correct": True}, {"text": "False"}], 'E', 'syllogism'),
            ("If '+' means 'x', '-' means '+', 'x' means '/' and '/' means '-', then 20 + 3 / 8 x 2 = ?", [{"text": "56", "is_correct": True}, {"text": "60"}, {"text": "52"}, {"text": "64"}], 'M', 'mathematical_logic'),
            ("Looking into a mirror, a clock shows 9:30. What is the actual time?", [{"text": "2:30", "is_correct": True}, {"text": "3:30"}, {"text": "4:30"}, {"text": "1:30"}], 'H', 'mirror_images'),
            ("How many triangles are there in a star shape?", [{"text": "5"}, {"text": "8"}, {"text": "10", "is_correct": True}, {"text": "12"}], 'M', 'visual_logic'),
            ("Which word cannot be formed from the letters of 'DETERMINATION'?", [{"text": "TERM"}, {"text": "NATION"}, {"text": "NATIVE", "is_correct": True}, {"text": "MINT"}], 'E', 'word_formation'),
            ("A man moves 4km West, turns left and moves 3km. How far is he from starting point?", [{"text": "5km", "is_correct": True}, {"text": "7km"}, {"text": "1km"}, {"text": "6km"}], 'E', 'directions'),
            ("Insert the missing number: 1, 4, 9, 16, 25, ?", [{"text": "30"}, {"text": "36", "is_correct": True}, {"text": "49"}, {"text": "40"}], 'E', 'number_series'),
            ("Find the missing letter: A, D, G, J, ?", [{"text": "L"}, {"text": "M", "is_correct": True}, {"text": "N"}, {"text": "O"}], 'E', 'alpha_series'),
            ("If 'SKY' is 'CLOUD', 'CLOUD' is 'RAIN', 'RAIN' is 'WATER', what do birds fly in?", [{"text": "SKY"}, {"text": "CLOUD", "is_correct": True}, {"text": "RAIN"}, {"text": "WATER"}], 'M', 'substitution'),
            ("Arrange in logical order: 1. Birth 2. Marriage 3. Education 4. Job 5. Death", [{"text": "1,3,4,2,5", "is_correct": True}, {"text": "1,2,3,4,5"}, {"text": "1,3,2,4,5"}, {"text": "1,4,3,2,5"}], 'E', 'sequencing'),
        ]
        for text, opts, diff, tag in sq: self.add_mcq(cat, text, opts, diff, tag)

    def seed_quantitative(self, cat):
        sq = [
            ("A sum of money doubles itself in 8 years at simple interest. Rate of interest is?", [{"text": "12.5%", "is_correct": True}, {"text": "10%"}, {"text": "15%"}, {"text": "20%"}], 'M', 'simple_interest'),
            ("The average of first 5 prime numbers is?", [{"text": "5.6", "is_correct": True}, {"text": "5.4"}, {"text": "5.8"}, {"text": "6.0"}], 'E', 'average'),
            ("If 15% of x = 20% of y, then x:y is?", [{"text": "4:3", "is_correct": True}, {"text": "3:4"}, {"text": "15:20"}, {"text": "20:15"}], 'E', 'ratio'),
            ("A train 240m long passes a pole in 24s. Its speed in km/h?", [{"text": "36", "is_correct": True}, {"text": "40"}, {"text": "45"}, {"text": "30"}], 'M', 'speed_distance'),
            ("In how many ways can 'APPLE' be arranged?", [{"text": "60", "is_correct": True}, {"text": "120"}, {"text": "24"}, {"text": "720"}], 'H', 'permutation'),
            ("Solve: 2^x = 64. Value of x?", [{"text": "6", "is_correct": True}, {"text": "5"}, {"text": "7"}, {"text": "8"}], 'E', 'indices'),
            ("A sells to B at 20% profit. B sells to C at 10% loss. Effective profit/loss?", [{"text": "8% profit", "is_correct": True}, {"text": "10% profit"}, {"text": "2% loss"}, {"text": "12% profit"}], 'M', 'profit_loss'),
            ("Probability of getting a sum of 7 when two dice are thrown?", [{"text": "1/6", "is_correct": True}, {"text": "1/12"}, {"text": "1/36"}, {"text": "1/18"}], 'H', 'probability'),
            ("Roots of x^2 - 5x + 6 = 0?", [{"text": "2, 3", "is_correct": True}, {"text": "-2, -3"}, {"text": "1, 6"}, {"text": "-1, -6"}], 'E', 'algebra'),
            ("Surface area of a sphere with radius 7 (pi=22/7)?", [{"text": "616", "is_correct": True}, {"text": "154"}, {"text": "308"}, {"text": "1232"}], 'M', 'geometry'),
            ("1/2 + 3/4 + 5/8 = ?", [{"text": "1 7/8", "is_correct": True}, {"text": "1 5/8"}, {"text": "2 1/8"}, {"text": "1 3/8"}], 'E', 'fractions'),
            ("Compound interest on 1000 for 2 years at 10% per annum?", [{"text": "210", "is_correct": True}, {"text": "200"}, {"text": "220"}, {"text": "1210"}], 'M', 'compound_interest'),
            ("If HCF and LCM of two numbers are 3 and 18, and one number is 9, find the other.", [{"text": "6", "is_correct": True}, {"text": "9"}, {"text": "12"}, {"text": "3"}], 'E', 'hcf_lcm'),
            ("Ratio of areas of two squares with sides 2:3?", [{"text": "4:9", "is_correct": True}, {"text": "2:3"}, {"text": "8:27"}, {"text": "1:2"}], 'E', 'mensuration'),
            ("Work done by A in 10 days, B in 15 days. Together they do it in?", [{"text": "6 days", "is_correct": True}, {"text": "7.5 days"}, {"text": "5 days"}, {"text": "6.5 days"}], 'E', 'time_work'),
        ]
        for text, opts, diff, tag in sq: self.add_mcq(cat, text, opts, diff, tag)

    def seed_verbal(self, cat):
        sq = [
            ("Choose synonym for 'ABUNDANT':", [{"text": "Plentiful", "is_correct": True}, {"text": "Scarce"}, {"text": "Cheap"}, {"text": "Rare"}], 'E', 'synonyms'),
            ("Choose antonym for 'OPTIMIST':", [{"text": "Pessimist", "is_correct": True}, {"text": "Realist"}, {"text": "Critic"}, {"text": "Idealist"}], 'E', 'antonyms'),
            ("Fill in blank: She ___ to the market yesterday.", [{"text": "went", "is_correct": True}, {"text": "goes"}, {"text": "gone"}, {"text": "going"}], 'E', 'tense'),
            ("One word substitution: A person who studies the stars.", [{"text": "Astronomer", "is_correct": True}, {"text": "Astrologer"}, {"text": "Astronaut"}, {"text": "Physicist"}], 'E', 'vocabulary'),
            ("Idiom meaning: 'Under the weather'?", [{"text": "Feeling sick", "is_correct": True}, {"text": "In the rain"}, {"text": "Upset"}, {"text": "Lucky"}], 'M', 'idioms'),
            ("Correct spelling:", [{"text": "Necessary", "is_correct": True}, {"text": "Necesary"}, {"text": "Neccessary"}, {"text": "Necasary"}], 'E', 'spelling'),
            ("Change to passive: 'He stole my purse'.", [{"text": "My purse was stolen by him", "is_correct": True}, {"text": "My purse stole him"}, {"text": "He was stolen by purse"}, {"text": "My purse is stolen"}], 'M', 'voice'),
            ("Select appropriate preposition: He died ___ cancer.", [{"text": "of", "is_correct": True}, {"text": "by"}, {"text": "with"}, {"text": "from"}], 'E', 'prepositions'),
            ("Find error: 'Every students was present'.", [{"text": "students (student)", "is_correct": True}, {"text": "was"}, {"text": "present"}, {"text": "No error"}], 'M', 'error_spotting'),
            ("Complete sentence: Although he is rich, ___.", [{"text": "he is unhappy", "is_correct": True}, {"text": "he is happy"}, {"text": "but he is unhappy"}, {"text": "yet he is happy"}], 'M', 'conjunctions'),
            ("Analogy: 'Author : Book :: Sculptor : ?'", [{"text": "Statue", "is_correct": True}, {"text": "Paint"}, {"text": "Stone"}, {"text": "Chisel"}], 'E', 'analogy'),
            ("Rearrange: (P) the (Q) boy (R) ran (S) fast.", [{"text": "PQRS", "is_correct": True}, {"text": "QPSR"}, {"text": "PRQS"}, {"text": "RPQS"}], 'E', 'sentence_ordering'),
            ("Synonym for 'ENIGMA':", [{"text": "Mystery", "is_correct": True}, {"text": "Answer"}, {"text": "Simple"}, {"text": "Ghost"}], 'M', 'synonyms'),
            ("Opposite of 'FRAGILE':", [{"text": "Strong", "is_correct": True}, {"text": "Weak"}, {"text": "Soft"}, {"text": "Broken"}], 'E', 'antonyms'),
            ("Fill gap: This is the man ___ I met yesterday.", [{"text": "whom", "is_correct": True}, {"text": "who"}, {"text": "which"}, {"text": "whose"}], 'M', 'pronouns'),
        ]
        for text, opts, diff, tag in sq: self.add_mcq(cat, text, opts, diff, tag)

    def seed_technical(self, cat):
        sq = [
            ("Which part is known as 'Brain of Computer'?", [{"text": "CPU", "is_correct": True}, {"text": "RAM"}, {"text": "HDD"}, {"text": "GPU"}], 'E', 'hardware'),
            ("Full form of HTTP?", [{"text": "HyperText Transfer Protocol", "is_correct": True}, {"text": "High Tech Text Process"}, {"text": "HyperText Type Protocol"}, {"text": "High Text Transfer Point"}], 'E', 'networking'),
            ("What is 'Python' in tech?", [{"text": "Programming Language", "is_correct": True}, {"text": "Snake"}, {"text": "Antivirus"}, {"text": "OS"}], 'E', 'programming'),
            ("Complexity of Binary Search?", [{"text": "O(log n)", "is_correct": True}, {"text": "O(n)"}, {"text": "O(n^2)"}, {"text": "O(1)"}], 'M', 'dsa'),
            ("Which is a volatile memory?", [{"text": "RAM", "is_correct": True}, {"text": "ROM"}, {"text": "EPROM"}, {"text": "Flash"}], 'E', 'memory'),
            ("What does HTML define?", [{"text": "Structure of webpage", "is_correct": True}, {"text": "Styling"}, {"text": "Logic"}, {"text": "Database"}], 'E', 'web_dev'),
            ("Who founded Microsoft?", [{"text": "Bill Gates", "is_correct": True}, {"text": "Steve Jobs"}, {"text": "Elon Musk"}, {"text": "Mark Zuckerberg"}], 'E', 'awareness'),
            ("Which is NOT an OS?", [{"text": "Java", "is_correct": True}, {"text": "Linux"}, {"text": "Windows"}, {"text": "Android"}], 'E', 'os'),
            ("Protocol for sending emails?", [{"text": "SMTP", "is_correct": True}, {"text": "FTP"}, {"text": "POP3"}, {"text": "IMAP"}], 'M', 'networking'),
            ("Unit of storage: 1KB = ___ bytes?", [{"text": "1024", "is_correct": True}, {"text": "1000"}, {"text": "8"}, {"text": "10240"}], 'E', 'basics'),
            ("Primary key in DB must be:", [{"text": "Unique & Not Null", "is_correct": True}, {"text": "Null"}, {"text": "Duplicate"}, {"text": "String only"}], 'M', 'database'),
            ("What is 'GitHub'?", [{"text": "Version Control Platform", "is_correct": True}, {"text": "Browser"}, {"text": "Compiler"}, {"text": "Database"}], 'E', 'awareness'),
            ("Which tag is used for line break in HTML?", [{"text": "<br>", "is_correct": True}, {"text": "<lb>"}, {"text": "<break>"}, {"text": "<hr>"}], 'E', 'web_dev'),
            ("Base of Hexadecimal number system?", [{"text": "16", "is_correct": True}, {"text": "10"}, {"text": "8"}, {"text": "2"}], 'M', 'binary'),
            ("What is '404' error?", [{"text": "Page Not Found", "is_correct": True}, {"text": "Server Error"}, {"text": "Forbidden"}, {"text": "Timeout"}], 'E', 'basics'),
        ]
        for text, opts, diff, tag in sq: self.add_mcq(cat, text, opts, diff, tag)

    def seed_arts(self, cat):
        sq = [
            ("Primary colors are:", [{"text": "Red, Yellow, Blue", "is_correct": True}, {"text": "Green, Orange, Violet"}, {"text": "Red, Green, Blue"}, {"text": "Yellow, Green, Cyan"}], 'E', 'color_theory'),
            ("Who painted the Mona Lisa?", [{"text": "Leonardo da Vinci", "is_correct": True}, {"text": "Picasso"}, {"text": "Van Gogh"}, {"text": "Michelangelo"}], 'E', 'history'),
            ("Opposite of 'Symmetry' is?", [{"text": "Asymmetry", "is_correct": True}, {"text": "Balance"}, {"text": "Order"}, {"text": "Pattern"}], 'E', 'principles'),
            ("Minimalist design focuses on:", [{"text": "Simplicity", "is_correct": True}, {"text": "Decoration"}, {"text": "Colors"}, {"text": "Complexity"}], 'E', 'design'),
            ("Mixing Red and Blue gives?", [{"text": "Purple/Violet", "is_correct": True}, {"text": "Green"}, {"text": "Orange"}, {"text": "Brown"}], 'E', 'color_theory'),
            ("Which period is 'Movable type' associated with?", [{"text": "Renaissance", "is_correct": True}, {"text": "Modern"}, {"text": "Medieval"}, {"text": "Baroque"}], 'M', 'history'),
            ("3D printing is also called:", [{"text": "Additive manufacturing", "is_correct": True}, {"text": "Subtractive modeling"}, {"text": "Laser cutting"}, {"text": "Molding"}], 'M', 'tech'),
            ("Golden Ratio value approx?", [{"text": "1.618", "is_correct": True}, {"text": "3.141"}, {"text": "2.718"}, {"text": "1.414"}], 'H', 'composition'),
            ("A 'Pantone' is a system for:", [{"text": "Color Matching", "is_correct": True}, {"text": "Font Design"}, {"text": "Image Editing"}, {"text": "Grid Layout"}], 'M', 'color_theory'),
            ("Sans-serif fonts differ from Serif fonts by:", [{"text": "Lack of small lines at ends", "is_correct": True}, {"text": "Using only capital letters"}, {"text": "Being italic"}, {"text": "Being thicker"}], 'E', 'typography'),
            ("Complementary color of Green?", [{"text": "Red", "is_correct": True}, {"text": "Yellow"}, {"text": "Blue"}, {"text": "Purple"}], 'M', 'color_theory'),
            ("Rule of Thirds is a technique for:", [{"text": "Composition", "is_correct": True}, {"text": "Lighting"}, {"text": "Symmetry"}, {"text": "Depth"}], 'M', 'composition'),
            ("A 'Logo' represents:", [{"text": "Brand Identity", "is_correct": True}, {"text": "Product Price"}, {"text": "Owner name"}, {"text": "Address"}], 'E', 'design'),
            ("Origami is the art of:", [{"text": "Paper folding", "is_correct": True}, {"text": "Sculpting stone"}, {"text": "Glass blowing"}, {"text": "Metal work"}], 'E', 'craft'),
            ("Visual balance where elements are equal around a center point?", [{"text": "Radial Balance", "is_correct": True}, {"text": "Linear Balance"}, {"text": "Asymmetric"}, {"text": "Grid"}], 'M', 'principles'),
        ]
        for text, opts, diff, tag in sq: self.add_mcq(cat, text, opts, diff, tag)

    def seed_personality(self, cat):
        traits = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]
        items = [
            ("I enjoy exploring new ideas and concepts.", "Openness"),
            ("I like to have everything organized and planned.", "Conscientiousness"),
            ("I feel energized after spending time with many people.", "Extraversion"),
            ("I am quick to sympathize with others' feelings.", "Agreeableness"),
            ("I get stressed easily in pressure situations.", "Neuroticism"),
            ("I prefer routine over unexpected changes.", "Openness"), # Reverse mapped usually but keeping simple
            ("I often leave my belongings scattered around.", "Conscientiousness"),
            ("I find it difficult to start conversations with strangers.", "Extraversion"),
            ("I believe that most people have good intentions.", "Agreeableness"),
            ("I am generally a relaxed person even in difficult times.", "Neuroticism"),
            ("I enjoy visiting art galleries or museums.", "Openness"),
            ("I set high goals for myself and work hard to achieve them.", "Conscientiousness"),
            ("I try to lead the group in social settings.", "Extraversion"),
            ("I am willing to compromise to avoid conflict.", "Agreeableness"),
            ("I often worry about things that might go wrong.", "Neuroticism"),
        ]
        for text, trait in items: self.add_likert(cat, text, trait)

    def seed_interest(self, cat):
        sq = [
            ("I enjoy working with tools and machinery.", [{"text": "Realistic", "riasec": "R", "is_correct": True}, {"text": "Not Interested"}], 'E', 'realistic'),
            ("I like to solve complex puzzles and research problems.", [{"text": "Investigative", "riasec": "I", "is_correct": True}, {"text": "Not Interested"}], 'E', 'investigative'),
            ("I love creating art, music, or writing stories.", [{"text": "Artistic", "riasec": "A", "is_correct": True}, {"text": "Not Interested"}], 'E', 'artistic'),
            ("I am passionate about helping people and teaching.", [{"text": "Social", "riasec": "S", "is_correct": True}, {"text": "Not Interested"}], 'E', 'social'),
            ("I enjoy leading teams and managing business projects.", [{"text": "Enterprising", "riasec": "E", "is_correct": True}, {"text": "Not Interested"}], 'E', 'enterprising'),
            ("I prefer working with data, numbers, and clear structures.", [{"text": "Conventional", "riasec": "C", "is_correct": True}, {"text": "Not Interested"}], 'E', 'conventional'),
            # Higher difficulty / Scenario
            ("Would you prefer fixing a broken appliance or reading a science journal?", [{"text": "Fixing appliance (R)", "riasec": "R", "is_correct": True}, {"text": "Reading journal (I)", "riasec": "I", "is_correct": True}], 'M', 'ri_choice'),
            ("Do you like designing a website (A) or coding its database (C)?", [{"text": "Designing (A)", "riasec": "A", "is_correct": True}, {"text": "Coding DB (C)", "riasec": "C", "is_correct": True}], 'M', 'ac_choice'),
            ("Starting a new business (E) vs Counseling a friend (S)?", [{"text": "Business (E)", "riasec": "E", "is_correct": True}, {"text": "Counseling (S)", "riasec": "S", "is_correct": True}], 'M', 'es_choice'),
            ("Building a model airplane.", [{"text": "Yes (R)", "riasec": "R", "is_correct": True}, {"text": "No"}], 'E', 'realistic'),
            ("Conducting chemical experiments.", [{"text": "Yes (I)", "riasec": "I", "is_correct": True}, {"text": "No"}], 'E', 'investigative'),
            ("Writing a play or poem.", [{"text": "Yes (A)", "riasec": "A", "is_correct": True}, {"text": "No"}], 'E', 'artistic'),
            ("Volunteering at a hospital.", [{"text": "Yes (S)", "riasec": "S", "is_correct": True}, {"text": "No"}], 'E', 'social'),
            ("Pitching an idea to investors.", [{"text": "Yes (E)", "riasec": "E", "is_correct": True}, {"text": "No"}], 'E', 'enterprising'),
            ("Keeping detailed financial records.", [{"text": "Yes (C)", "riasec": "C", "is_correct": True}, {"text": "No"}], 'E', 'conventional'),
        ]
        for text, opts, diff, tag in sq: self.add_mcq(cat, text, opts, diff, tag)

    def seed_values(self, cat):
        items = [
            ("I value having a clear work-life balance.", "work_life_balance"),
            ("Being creative at work is very important to me.", "creativity"),
            ("I want a career that offers high financial rewards.", "wealth"),
            ("It is important that my work helps society.", "helping_society"),
            ("I prefer job security and stability over high risk.", "stability"),
            ("I want to be in a position of power and influence.", "power"),
            ("I enjoy working in a team rather than alone.", "teamwork"),
            ("I value having the freedom to set my own hours.", "independence"),
            ("I want my work to be recognized by others.", "recognition"),
            ("I enjoy constantly learning new skills.", "growth"),
            ("I am willing to work long hours for career growth.", "ambition"),
            ("I prefer a quiet and calm working environment.", "environment"),
            ("I value variety and change in my daily tasks.", "variety"),
            ("I want to work for a company with strong ethics.", "ethics"),
            ("Distance from home is a major factor in my job choice.", "convenience"),
        ]
        for text, tag in items: self.add_likert(cat, text, tag)
