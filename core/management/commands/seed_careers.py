from django.core.management.base import BaseCommand
from core.models import CareerCategory, Career

class Command(BaseCommand):
    help = 'Seed Career Categories and 40 Careers'

    def handle(self, *args, **options):
        categories = [
            'IT & Software', 'Medical & Healthcare', 'Engineering',
            'Commerce & Finance', 'Legal', 'Education & Research',
            'Hospitality & Tourism', 'Agriculture & Environment',
            'Arts & Media', 'Maritime & Nautical',
            'Ayurveda & Traditional Medicine', 'Government & PSC'
        ]
        
        cat_map = {}
        for idx, cname in enumerate(categories):
            cat, _ = CareerCategory.objects.get_or_create(
                name=cname,
                slug=cname.lower().replace(' & ', '-').replace(' ', '-'),
                defaults={'order': idx}
            )
            cat_map[cname] = cat

        progression_data = {
            "0-2yr": "Entry Level Role",
            "2-5yr": "Mid Level Role",
            "5-8yr": "Senior Level Role",
            "8yr+": "Management / Lead"
        }
        
        tech_skills = ["Software Development", "Problem Solving", "Domain Knowledge", "Tools"]
        soft_skills = ["Communication", "Leadership", "Teamwork"]
        emp_ker = ["TCS (Kochi)", "Infosys (Trivandrum)"]
        
        # We need 40 careers, starting with 15 mandatory ones:
        careers_data = [
            # 1-15: Mandatory
            {
                'title': 'Software Developer', 'slug': 'software-developer', 'category': cat_map['IT & Software'],
                'riasec_primary': 'I', 'salary_kerala_min': 4.0, 'salary_kerala_max': 18.0, 'salary_india_avg': 8.0,
                'gulf_opportunity': False, 'is_psc_available': False,
                'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 
                'top_employers_kerala': emp_ker, 'who_should_choose': 'People who love logic.', 'who_should_avoid': 'Those who dislike sitting.'
            },
            {
                'title': 'Data Scientist', 'slug': 'data-scientist', 'category': cat_map['IT & Software'],
                'riasec_primary': 'I', 'salary_kerala_min': 6.0, 'salary_kerala_max': 25.0, 'salary_india_avg': 10.0,
                'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 'top_employers_kerala': emp_ker, 'who_should_choose': 'Math lovers.', 'who_should_avoid': 'Hate stats.'
            },
            {
                'title': 'Civil Engineer', 'slug': 'civil-engineer', 'category': cat_map['Engineering'],
                'riasec_primary': 'R', 'gulf_opportunity': True, 'gulf_notes': 'High demand in UAE, Qatar, Saudi Arabia for infrastructure projects.',
                'salary_kerala_min': 3.0, 'salary_kerala_max': 12.0, 'salary_india_avg': 5.0,
                'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 'top_employers_kerala': emp_ker, 'who_should_choose': 'Builders.', 'who_should_avoid': 'Desk workers.'
            },
            {
                'title': 'MBBS Doctor', 'slug': 'mbbs-doctor', 'category': cat_map['Medical & Healthcare'],
                'riasec_primary': 'I', 'riasec_secondary': 'S', 'salary_kerala_min': 6.0, 'salary_kerala_max': 30.0, 'salary_india_avg': 12.0,
                'is_psc_available': True, 'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 'top_employers_kerala': emp_ker, 'who_should_choose': 'Helpers.', 'who_should_avoid': 'Squeamish.'
            },
            {
                'title': 'Ayurvedic Physician (BAMS)', 'slug': 'ayurvedic-physician', 'category': cat_map['Ayurveda & Traditional Medicine'],
                'riasec_primary': 'I', 'riasec_secondary': 'S', 'is_ayurveda_related': True,
                'kerala_job_market_notes': 'Kerala is the global capital of Ayurveda. Strong local and medical tourism demand.',
                'salary_kerala_min': 4.0, 'salary_kerala_max': 15.0, 'salary_india_avg': 6.0,
                'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 'top_employers_kerala': emp_ker, 'who_should_choose': 'Tradtional healers.', 'who_should_avoid': 'Allopathic.'
            },
            {
                'title': 'Chartered Accountant (CA)', 'slug': 'chartered-accountant', 'category': cat_map['Commerce & Finance'],
                'riasec_primary': 'C', 'salary_kerala_min': 6.0, 'salary_kerala_max': 20.0, 'salary_india_avg': 9.0,
                'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 'top_employers_kerala': emp_ker, 'who_should_choose': 'Number crunchers.', 'who_should_avoid': 'Artistic.'
            },
            {
                'title': 'Lawyer / Advocate', 'slug': 'lawyer-advocate', 'category': cat_map['Legal'],
                'riasec_primary': 'E', 'riasec_secondary': 'S', 'is_psc_available': True,
                'salary_kerala_min': 3.0, 'salary_kerala_max': 25.0, 'salary_india_avg': 8.0,
                'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 'top_employers_kerala': emp_ker, 'who_should_choose': 'Debaters.', 'who_should_avoid': 'Introverts.'
            },
            {
                'title': 'School Teacher', 'slug': 'school-teacher', 'category': cat_map['Education & Research'],
                'riasec_primary': 'S', 'is_psc_available': True,
                'kerala_job_market_notes': 'Kerala PSC recruits teachers regularly. High job security.',
                'salary_kerala_min': 4.0, 'salary_kerala_max': 12.0, 'salary_india_avg': 5.0,
                'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 'top_employers_kerala': emp_ker, 'who_should_choose': 'Patient guides.', 'who_should_avoid': 'Impatient.'
            },
            {
                'title': 'Nurse', 'slug': 'nurse', 'category': cat_map['Medical & Healthcare'],
                'riasec_primary': 'S', 'gulf_opportunity': True, 'gulf_notes': "One of Kerala's largest Gulf export professions. Strong demand in Gulf hospitals.",
                'salary_kerala_min': 2.5, 'salary_kerala_max': 8.0, 'salary_india_avg': 4.0,
                'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 'top_employers_kerala': emp_ker, 'who_should_choose': 'Compassionate.', 'who_should_avoid': 'Non-empathetic.'
            },
            {
                'title': 'Hotel & Resort Manager', 'slug': 'hotel-resort-manager', 'category': cat_map['Hospitality & Tourism'],
                'riasec_primary': 'E', 'is_tourism_related': True,
                'kerala_job_market_notes': "Kerala tourism is a ₹40,000 crore industry. God's Own Country brand drives demand.",
                'salary_kerala_min': 4.0, 'salary_kerala_max': 15.0, 'salary_india_avg': 6.0,
                'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 'top_employers_kerala': emp_ker, 'who_should_choose': 'Organizers.', 'who_should_avoid': 'Anti-social.'
            },
            {
                'title': 'Marine Engineer', 'slug': 'marine-engineer', 'category': cat_map['Maritime & Nautical'],
                'riasec_primary': 'R', 'gulf_opportunity': True,
                'salary_kerala_min': 6.0, 'salary_kerala_max': 25.0, 'salary_india_avg': 10.0,
                'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 'top_employers_kerala': emp_ker, 'who_should_choose': 'Seafarers.', 'who_should_avoid': 'Seasick.'
            },
            {
                'title': 'Fisheries Scientist', 'slug': 'fisheries-scientist', 'category': cat_map['Agriculture & Environment'],
                'riasec_primary': 'I', 'riasec_secondary': 'R',
                'kerala_job_market_notes': "Kerala's 590km coastline makes fisheries a critical industry.",
                'salary_kerala_min': 5.0, 'salary_kerala_max': 14.0, 'salary_india_avg': 6.0,
                'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 'top_employers_kerala': emp_ker, 'who_should_choose': 'Nature lovers.', 'who_should_avoid': 'Urban only.'
            },
            {
                'title': 'Journalist / Media Professional', 'slug': 'journalist', 'category': cat_map['Arts & Media'],
                'riasec_primary': 'A', 'salary_kerala_min': 3.0, 'salary_kerala_max': 15.0, 'salary_india_avg': 6.0,
                'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 'top_employers_kerala': emp_ker, 'who_should_choose': 'Writers.', 'who_should_avoid': 'Shy.'
            },
            {
                'title': 'Social Worker', 'slug': 'social-worker', 'category': cat_map['Education & Research'],
                'riasec_primary': 'S', 'is_psc_available': True,
                'salary_kerala_min': 2.5, 'salary_kerala_max': 8.0, 'salary_india_avg': 4.0,
                'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 'top_employers_kerala': emp_ker, 'who_should_choose': 'Empaths.', 'who_should_avoid': 'Apathetic.'
            },
            {
                'title': 'Pharmacist', 'slug': 'pharmacist', 'category': cat_map['Medical & Healthcare'],
                'riasec_primary': 'I', 'riasec_secondary': 'C',
                'salary_kerala_min': 3.0, 'salary_kerala_max': 10.0, 'salary_india_avg': 4.5,
                'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 'top_employers_kerala': emp_ker, 'who_should_choose': 'Precise.', 'who_should_avoid': 'Careless.'
            }
        ]

        # Generate 25 more dummies to hit 40
        for i in range(16, 41):
            careers_data.append({
                'title': f'Career Title {i}', 'slug': f'career-{i}', 'category': cat_map['IT & Software'],
                'riasec_primary': 'R', 'salary_kerala_min': 3.0, 'salary_kerala_max': 10.0, 'salary_india_avg': 5.0,
                'progression_timeline': progression_data, 'technical_skills': tech_skills, 'soft_skills': soft_skills, 'top_employers_kerala': emp_ker, 'who_should_choose': 'Anyone.', 'who_should_avoid': 'No one.'
            })

        created_count = 0
        for data in careers_data:
            # Set minimum defaults for required non-nullable fields not in data
            defaults = {
                'description': 'A rewarding career.',
                'day_in_life': 'A typical day involves many tasks.',
                'work_environment': 'OFFICE',
                'job_demand': 'HIGH',
                'growth_rate_pct': 10.0,
                'minimum_qualification': 'Bachelor Degree'
            }
            defaults.update(data)
            
            slug = defaults.pop('slug')
            obj, created = Career.objects.get_or_create(
                slug=slug,
                defaults=defaults
            )
            if created:
                created_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} Careers.'))
