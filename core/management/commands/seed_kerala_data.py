import datetime
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from core.models import CAPRound, PSCDepartment, PSCPost, GulfCountry, GulfCareerOpportunity
from core.models import Career

class Command(BaseCommand):
    help = 'Seeds data for Kerala-specific modules (CAP, PSC, Gulf)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Kerala data seeding...")

        # Section A: CAPRounds
        # Round 1
        CAPRound.objects.get_or_create(
            round_number=1,
            academic_year="2024-2025",
            defaults={
                'registration_start': datetime.date(2024, 1, 15),
                'registration_end': datetime.date(2024, 2, 15),
                'allotment_date': datetime.date(2024, 3, 1),
                'fee_payment_deadline': datetime.date(2024, 3, 7),
                'reporting_start': datetime.date(2024, 3, 8),
                'reporting_end': datetime.date(2024, 3, 10),
                'notes': "Candidates must report with original certificates",
            }
        )
        # Round 2
        CAPRound.objects.get_or_create(
            round_number=2,
            academic_year="2024-2025",
            defaults={
                'registration_start': datetime.date(2024, 3, 15),
                'registration_end': datetime.date(2024, 4, 1),
                'allotment_date': datetime.date(2024, 4, 15),
                'fee_payment_deadline': datetime.date(2024, 4, 20),
                'reporting_start': datetime.date(2024, 4, 21),
                'reporting_end': datetime.date(2024, 4, 23),
            }
        )
        # Round 3
        CAPRound.objects.get_or_create(
            round_number=3,
            academic_year="2024-2025",
            defaults={
                'registration_start': datetime.date(2024, 5, 1),
                'registration_end': datetime.date(2024, 5, 15),
                'allotment_date': datetime.date(2024, 6, 1),
                'fee_payment_deadline': datetime.date(2024, 6, 5),
                'reporting_start': datetime.date(2024, 6, 6),
                'reporting_end': datetime.date(2024, 6, 8),
            }
        )

        # Section B: PSC Departments
        departments = [
            "Kerala Public Service Commission (General)",
            "Kerala Education Department",
            "Kerala Police Department",
            "Kerala Health Services",
            "Kerala PWD (Public Works Department)",
            "Kerala Forest Department",
            "Kerala Revenue Department",
            "Kerala Judiciary",
        ]
        for dept in departments:
            PSCDepartment.objects.get_or_create(
                name=dept,
                slug=slugify(dept)
            )

        # Helper
        def get_dept(name):
            return PSCDepartment.objects.get(name=name)

        # Section C: PSC Posts
        psc_data = [
            {
                "title": "Lower Division Clerk (LDC)",
                "dept": "Kerala Public Service Commission (General)",
                "pay_scale": "₹19,000-₹43,600",
                "eligibility_education": "SSLC / 10th Standard or equivalent",
            },
            {
                "title": "Assistant Professor",
                "dept": "Kerala Education Department",
                "pay_scale": "₹57,700-₹1,12,400",
                "eligibility_education": "PG degree in relevant subject + NET/SET",
            },
            {
                "title": "Sub Inspector of Police",
                "dept": "Kerala Police Department",
                "pay_scale": "₹41,500-₹87,000",
                "eligibility_education": "Degree from recognized university",
                "qualifying_exam": "PSC Written Test + Physical Measurement + Interview",
            },
            {
                "title": "Staff Nurse",
                "dept": "Kerala Health Services",
                "pay_scale": "₹29,200-₹62,400",
                "eligibility_education": "BSc Nursing or GNM and Kerala Nurses and Midwives Council Registration",
            },
            {
                "title": "Assistant Engineer (Civil)",
                "dept": "Kerala PWD (Public Works Department)",
                "pay_scale": "₹36,600-₹79,200",
                "eligibility_education": "B.Tech / BE in Civil Engineering",
            },
            {
                "title": "Forest Guard",
                "dept": "Kerala Forest Department",
                "pay_scale": "₹19,900-₹46,400",
                "eligibility_education": "Plus Two/12th Standard and prescribed physical standards",
            },
            {
                "title": "Village Field Assistant",
                "dept": "Kerala Revenue Department",
                "pay_scale": "₹19,000-₹43,600",
                "eligibility_education": "SSLC pass or equivalent",
            },
            {
                "title": "Munsiff Magistrate",
                "dept": "Kerala Judiciary",
                "pay_scale": "₹77,400-₹1,15,200",
                "eligibility_education": "LLB degree and enrolled as an Advocate",
            },
            {
                "title": "High School Teacher (various subjects)",
                "dept": "Kerala Education Department",
                "pay_scale": "₹32,300-₹68,700",
                "eligibility_education": "Degree in subject + B.Ed/TTC + KTET",
            },
            {
                "title": "Junior Public Health Nurse",
                "dept": "Kerala Health Services",
                "pay_scale": "₹25,200-₹54,000",
                "eligibility_education": "Auxiliary Nurse Midwifery Course (ANM) certificate",
            },
            {
                "title": "Agricultural Officer",
                "dept": "Kerala Public Service Commission (General)",
                "pay_scale": "₹39,500-₹83,000",
                "eligibility_education": "BSc Agriculture",
            },
            {
                "title": "Ayurveda Medical Officer",
                "dept": "Kerala Health Services",
                "pay_scale": "₹55,200-₹1,15,300",
                "eligibility_education": "BAMS Degree and enrollment in Medical Council",
            },
            {
                "title": "Veterinary Surgeon",
                "dept": "Kerala Public Service Commission (General)",
                "pay_scale": "₹55,200-₹1,15,300",
                "eligibility_education": "BVSc & AH Degree",
            },
            {
                "title": "Pharmacist (Grade II)",
                "dept": "Kerala Health Services",
                "pay_scale": "₹27,900-₹63,700",
                "eligibility_education": "Diploma in Pharmacy (D.Pharm)",
            },
            {
                "title": "Police Constable",
                "dept": "Kerala Police Department",
                "pay_scale": "₹22,200-₹48,000",
                "eligibility_education": "SSLC/10th Pass + Physical standard tests",
            },
        ]

        for p in psc_data:
            PSCPost.objects.get_or_create(
                title=p["title"],
                department=get_dept(p["dept"]),
                defaults={
                    'slug': slugify(p["title"]),
                    'pay_scale': p["pay_scale"],
                    'eligibility_education': p["eligibility_education"],
                    'eligibility_age': "18-36 years (relaxation for reserved categories)",
                    'qualifying_exam': p.get("qualifying_exam", "PSC Written Exam"),
                }
            )

        # Section D: Gulf Countries
        gulf_countries = [
            ("UAE", "🇦🇪", "AED", 18.0, 1200000, ["Construction","Healthcare","IT","Hospitality","Finance"]),
            ("Qatar", "🇶🇦", "QAR", 20.0, 700000, ["Construction","LNG/Energy","Healthcare","Education"]),
            ("Saudi Arabia", "🇸🇦", "SAR", 16.0, 1000000, ["Construction","Oil & Gas","Healthcare","Retail"]),
            ("Kuwait", "🇰🇼", "KWD", 22.0, 300000, ["Oil & Gas","Healthcare","Construction"]),
            ("Bahrain", "🇧🇭", "BHD", 15.0, 150000, ["Finance","Healthcare","Hospitality"]),
            ("Oman", "🇴🇲", "OMR", 14.0, 400000, ["Construction","Healthcare","Education","Retail"]),
        ]
        for name, flag, curr, sp, workers, sectors in gulf_countries:
            GulfCountry.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'flag_emoji': flag,
                    'currency': curr,
                    'avg_salary_inr_lpa': sp,
                    'kerala_workers_estimate': workers,
                    'popular_sectors': sectors,
                }
            )

        def get_country(name):
            return GulfCountry.objects.get(name=name)

        # Section E: Gulf Career Opportunities
        opp_data = [
            ("Nurse", "UAE", "HIGH", 22.0, ["HAAD License","DHA License","MOH License"], ""),
            ("Nurse", "Qatar", "HIGH", 24.0, ["QCHP Registration"], ""),
            ("Civil Engineer", "UAE", "HIGH", 25.0, [], ""),
            ("Civil Engineer", "Qatar", "HIGH", 28.0, [], ""),
            ("Software Developer", "UAE", "MEDIUM", 30.0, [], ""),
            ("Hotel & Resort Manager", "UAE", "MEDIUM", 20.0, [], ""),
            ("Pharmacist", "UAE", "HIGH", 24.0, ["DHA License","MOH License"], ""),
            ("Marine Engineer", "UAE", "MEDIUM", 26.0, [], ""),
            ("Ayurvedic Physician", "UAE", "LOW", 18.0, [], "Growing wellness tourism demand in Dubai"),
            ("Social Worker", "Qatar", "LOW", 16.0, [], ""),
            ("Accountant", "UAE", "MEDIUM", 22.0, [], ""),
            ("Teacher", "UAE", "MEDIUM", 16.0, ["KHDA/ADEC certification required"], "KHDA certification preferred"),
        ]

        for career_search, country_name, demand, salary, certs, notes in opp_data:
            career = Career.objects.filter(title__icontains=career_search).first()
            if not career:
                self.stdout.write(self.style.WARNING(f"Career not found: {career_search}. Skipping Gulf Opportunity."))
                continue

            GulfCareerOpportunity.objects.get_or_create(
                career=career,
                country=get_country(country_name),
                defaults={
                    'avg_salary_inr_lpa': salary,
                    'demand_level': demand,
                    'required_certifications': certs,
                    'notes': notes,
                }
            )

        self.stdout.write(self.style.SUCCESS("✅ CAP Rounds: 3 seeded"))
        self.stdout.write(self.style.SUCCESS("✅ PSC Departments: 8 seeded"))
        self.stdout.write(self.style.SUCCESS("✅ PSC Posts: 15 seeded"))
        self.stdout.write(self.style.SUCCESS("✅ Gulf Countries: 6 seeded"))
        self.stdout.write(self.style.SUCCESS("✅ Gulf Opportunities: 12 seeded"))
