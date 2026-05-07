from django.core.management.base import BaseCommand
from django.utils.text import slugify
from core.models import Stream, Field, Discipline, Course, Specialization

class Command(BaseCommand):
    help = 'Seeds taxonomy hierarchy: Streams, Fields, Disciplines, Courses, Specializations'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting taxonomy seed...")

        # 1. Streams (>= 10)
        streams_data = [
            ("Engineering & Technology", "#FF5733", 1),
            ("Science & Research", "#33FFE0", 2),
            ("Medicine & Health Sciences", "#FF33A8", 3),
            ("Arts, Humanities & Social Sciences", "#D433FF", 4),
            ("Commerce & Business", "#33C1FF", 5),
            ("Law & Legal Studies", "#FFC733", 6),
            ("Design & Architecture", "#80FF33", 7),
            ("Media & Mass Communication", "#FF8633", 8),
            ("Agriculture & Allied Sciences", "#33FF7A", 9),
            ("Education & Teaching", "#A833FF", 10),
            ("Hospitality & Tourism", "#FF3333", 11),
        ]
        
        for name, color, order in streams_data:
            Stream.objects.get_or_create(
                name=name, 
                defaults={
                    'slug': slugify(name), 
                    'description': f"Streams for {name}", 
                    'suitable_for': "All students",
                    'color_code': color, 
                    'order': order
                }
            )

        # 2. Fields (>= 15)
        fields_data = [
            ("Computer Science", "Engineering & Technology"), ("Mechanical & Auto", "Engineering & Technology"),
            ("Civil & Architecture", "Engineering & Technology"), ("Electronics & Electrical", "Engineering & Technology"),
            ("Physics & Math", "Science & Research"), ("Life Sciences", "Science & Research"),
            ("Chemistry & Material", "Science & Research"), ("Allopathic Medicine", "Medicine & Health Sciences"),
            ("Alternative Medicine", "Medicine & Health Sciences"), ("Allied Health", "Medicine & Health Sciences"),
            ("Literature & Languages", "Arts, Humanities & Social Sciences"), ("Social Sciences", "Arts, Humanities & Social Sciences"),
            ("Finance & Accounting", "Commerce & Business"), ("Management & Administration", "Commerce & Business"),
            ("Corporate Law", "Law & Legal Studies"), ("Criminal Law", "Law & Legal Studies"),
            ("Interior & Fashion", "Design & Architecture"), ("Visual Arts", "Design & Architecture"),
            ("Journalism", "Media & Mass Communication"), ("Agriculture & Farming", "Agriculture & Allied Sciences")
        ]
        
        for fname, sname in fields_data:
            stream = Stream.objects.get(name=sname)
            Field.objects.update_or_create(name=fname, stream=stream, defaults={'slug': slugify(fname)})

        # 3. Disciplines (>= 25)
        disciplines_data = [
            ("Software Engineering", "Computer Science", ['logical', 'technical']), ("Data Science", "Computer Science", ['logical', 'quantitative', 'technical']),
            ("Cyber Security", "Computer Science", ['logical', 'technical']), ("Mechanical Engineering", "Mechanical & Auto", ['logical', 'technical']),
            ("Automobile Engineering", "Mechanical & Auto", ['logical', 'technical']), ("Civil Engineering", "Civil & Architecture", ['technical', 'quantitative']),
            ("Architecture", "Civil & Architecture", ['arts', 'technical']), ("Electrical Engineering", "Electronics & Electrical", ['logical', 'technical']),
            ("Electronics Engineering", "Electronics & Electrical", ['logical', 'technical']), ("Applied Physics", "Physics & Math", ['logical', 'quantitative']),
            ("Mathematics", "Physics & Math", ['quantitative', 'logical']), ("Biotechnology", "Life Sciences", ['logical', 'technical']),
            ("Microbiology", "Life Sciences", ['logical']), ("Organic Chemistry", "Chemistry & Material", ['logical']),
            ("MBBS", "Allopathic Medicine", ['logical', 'verbal']), ("Dentistry", "Allopathic Medicine", ['logical', 'technical']),
            ("Ayurveda", "Alternative Medicine", ['logical', 'verbal']), ("Nursing", "Allied Health", ['verbal']),
            ("Pharmacy", "Allied Health", ['logical', 'quantitative']), ("English Literature", "Literature & Languages", ['verbal', 'arts']),
            ("History", "Social Sciences", ['verbal']), ("Sociology", "Social Sciences", ['verbal']),
            ("Psychology", "Social Sciences", ['verbal', 'logical']), ("Chartered Accountancy", "Finance & Accounting", ['quantitative', 'logical']),
            ("Business Administration", "Management & Administration", ['verbal', 'logical']), ("Human Resources", "Management & Administration", ['verbal']),
            ("Tax Law", "Corporate Law", ['verbal', 'logical']), ("Criminal Law", "Criminal Law", ['verbal', 'logical']),
            ("Fashion Design", "Interior & Fashion", ['arts']), ("Graphic Design", "Visual Arts", ['arts']),
            ("Broadcast Journalism", "Journalism", ['verbal', 'arts']), ("Agronomy", "Agriculture & Farming", ['logical', 'technical'])
        ]
        
        for dname, fname, tags in disciplines_data:
            field = Field.objects.get(name=fname)
            Discipline.objects.update_or_create(
                name=dname, field=field, 
                defaults={'slug': slugify(dname), 'overview': f"Overview of {dname}", 'aptitude_tags': tags}
            )

        # 4. Courses (>= 60)
        course_levels = {'B.Tech': 'UG', 'M.Tech': 'PG', 'B.Sc': 'UG', 'M.Sc': 'PG', 'BA': 'UG', 'MA': 'PG', 'BBA': 'UG', 'MBA': 'PG', 'B.Com': 'UG', 'M.Com': 'PG', 'LLB': 'UG', 'LLM': 'PG', 'B.Des': 'UG', 'M.Des': 'PG', 'B.Arch': 'UG', 'M.Arch': 'PG', 'BDS': 'UG', 'MDS': 'PG', 'BAMS': 'UG', 'B.Sc Nursing': 'UG', 'B.Pharm': 'UG', 'M.Pharm': 'PG', 'B.J.M.C.': 'UG', 'M.J.M.C.': 'PG'}
        
        # Helper to get level from name
        def get_level(cname):
            for prefix, level in course_levels.items():
                if cname.startswith(prefix): return level
            return 'UG'

        courses_to_seed = []
        for d in Discipline.objects.all():
            courses_to_seed.append(f"B.Tech {d.name}")
            courses_to_seed.append(f"M.Tech {d.name}")

        extra_courses = [
            "B.Sc Physics", "M.Sc Physics", "B.Sc Chemistry", "M.Sc Chemistry",
            "B.Sc Mathematics", "M.Sc Mathematics", "BA English", "MA English",
            "BA History", "MA History", "BA Sociology", "MA Sociology",
            "BBA", "MBA", "B.Com", "M.Com", "LLB", "LLM", "B.Des Fashion", "M.Des Fashion",
            "B.Sc Agriculture", "M.Sc Agriculture", "BCA", "MCA", "B.Arch", "M.Arch",
            "BDS", "MDS", "BAMS", "B.Sc Nursing", "B.Pharm", "M.Pharm", "B.J.M.C.", "M.J.M.C.",
            "MBBS", "BDS" # Ensure these are there
        ]
        courses_to_seed.extend(extra_courses)
        
        for cname in set(courses_to_seed):
            level = get_level(cname)
            # Improved discipline matching
            matching_d = None
            for d in Discipline.objects.all():
                if d.name.lower() in cname.lower():
                    matching_d = d
                    break
            
            if not matching_d:
                # Fallback to field match or stream match if naming is tricky
                matching_d = Discipline.objects.first()
            
            Course.objects.update_or_create(
                name=cname, discipline=matching_d, 
                defaults={
                    'slug': slugify(cname), 
                    'level': level, 
                    'duration_years': 5.0 if 'Architecture' in cname or 'MBBS' in cname else (4.0 if level == 'UG' else 2.0),
                    'description': f"Course description for {cname}",
                    'eligibility_description': "12th Pass" if level == 'UG' else "Degree Pass"
                }
            )

        # 5. Specializations (>= 20)
        specs_data = [
            ("AI & Machine Learning", "B.Tech Software"), ("Cloud Computing", "B.Tech Software"),
            ("Data Science", "B.Tech Software"), ("Cyber Security", "B.Tech Software"),
            ("Structural Engineering", "Civil Engineering"), ("Construction Management", "Civil Engineering"),
            ("Geotechnical Engineering", "Civil Engineering"), ("Thermal Engineering", "Mechanical Engineering"),
            ("Robotics", "Mechanical Engineering"), ("Power Systems", "Electrical Engineering"),
            ("Control Systems", "Electrical Engineering"), ("VLSI Design", "Electronics"),
            ("Embedded Systems", "Electronics"), ("Clinical Psychology", "Psychology"),
            ("Counseling Psychology", "Psychology"), ("Finance", "MBA"), ("Marketing", "MBA"),
            ("HR", "MBA"), ("Operations", "MBA"), ("Supply Chain", "MBA"),
            ("Cyber Law", "LLM"), ("Tax Law", "LLM"), ("IPR Law", "LLM"),
            ("Cardiology", "MBBS"), ("Neurology", "MBBS"), ("Orthopedics", "MBBS"),
            ("Dermatology", "MBBS"), ("Pediatrics", "MBBS"), ("Orthodontics", "BDS"),
            ("Oral Surgery", "BDS"), ("Kayachikitsa", "BAMS"), ("Panchakarma", "BAMS"),
        ]
        
        for sname, cname_frag in specs_data:
            course = Course.objects.filter(name__icontains=cname_frag).first()
            if course:
                Specialization.objects.update_or_create(
                    name=sname, course=course, 
                    defaults={
                        'description': f"Specialization in {sname}",
                        'job_demand': 'HIGH'
                    }
                )

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded Taxonomy: {Stream.objects.count()} Streams, {Field.objects.count()} Fields, {Discipline.objects.count()} Disciplines, {Course.objects.count()} Courses, {Specialization.objects.count()} Specializations."))
