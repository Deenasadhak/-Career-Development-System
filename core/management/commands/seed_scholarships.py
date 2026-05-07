from django.core.management.base import BaseCommand
from core.models import Scholarship

class Command(BaseCommand):
    help = 'Seed Scholarships'

    def handle(self, *args, **options):
        scholarships = [
            {
                'name': 'Post-Matric Scholarship (SC/ST)', 'slug': 'post-matric-sc-st',
                'offering_organization': 'Kerala SC/ST Development Corporation',
                'scholarship_type': 'COMMUNITY', 'eligible_communities': ["SC", "ST"],
                'income_ceiling_annual': 250000, 'amount_per_year': 15000,
                'documents_required': ["Caste Certificate","Income Certificate","Mark Sheet","Bank Passbook"],
                'is_kerala_specific': True
            },
            {
                'name': 'DCMS Merit Scholarship', 'slug': 'dcms-merit',
                'offering_organization': 'Directorate of Collegiate Education, Kerala',
                'scholarship_type': 'MERIT', 'eligible_communities': [],
                'min_percentage_required': 80.0, 'amount_per_year': 10000,
                'is_kerala_specific': True
            },
            {
                'name': 'KSCBC Scholarship', 'slug': 'kscbc',
                'offering_organization': 'Kerala State Backward Classes Development Corp',
                'scholarship_type': 'COMMUNITY', 'eligible_communities': ["OBC","OBC_H","EZHAVA","NAIR","VISWAKARMA","LATIN_CATHOLIC","OTHER_CHRISTIAN"],
                'income_ceiling_annual': 600000, 'amount_per_year': 12000,
                'is_kerala_specific': True
            },
            {
                'name': 'Minority Welfare Scholarship', 'slug': 'minority-welfare',
                'offering_organization': 'Kerala Minority Welfare Department',
                'scholarship_type': 'COMMUNITY', 'eligible_communities': ["MUSLIM","LATIN_CATHOLIC","OTHER_CHRISTIAN"],
                'income_ceiling_annual': 600000, 'amount_per_year': 10000,
                'is_kerala_specific': True
            },
            {
                'name': 'Kerala Fishermen Welfare Fund Scholarship', 'slug': 'fishermen-welfare',
                'offering_organization': 'Kerala Fishermen Welfare Fund Board',
                'scholarship_type': 'NEED', 'eligible_communities': [],
                'amount_per_year': 8000, 'description': 'Condition: parent must be registered fisherman',
                'is_kerala_specific': True
            },
            {
                'name': 'National Scholarship Portal — Post Matric', 'slug': 'nsp-post-matric',
                'offering_organization': 'Ministry of Social Justice, GoI',
                'scholarship_type': 'GOVT', 'eligible_communities': ["SC","ST","OBC","EWS"],
                'income_ceiling_annual': 250000, 'amount_per_year': 20000,
                'application_portal': 'https://scholarships.gov.in',
                'is_kerala_specific': False
            },
            {
                'name': 'AICTE Pragati Scholarship (Girls)', 'slug': 'aicte-pragati',
                'offering_organization': 'AICTE',
                'scholarship_type': 'GIRL_CHILD', 'is_girl_only': True,
                'income_ceiling_annual': 800000, 'amount_per_year': 50000,
                'is_kerala_specific': False
            },
            {
                'name': 'Prime Minister Scholarship Scheme (PMSS)', 'slug': 'pmss',
                'offering_organization': 'Ministry of Home Affairs, GoI',
                'scholarship_type': 'GOVT', 'amount_per_year': 36000,
                'description': 'Children of ex-servicemen / paramilitary',
                'is_kerala_specific': False
            },
            {
                'name': 'INSPIRE Scholarship (DST)', 'slug': 'inspire',
                'offering_organization': 'Department of Science & Technology, GoI',
                'scholarship_type': 'MERIT', 'min_percentage_required': 80.0,
                'amount_per_year': 80000,
                'is_kerala_specific': False
            },
            {
                'name': 'EWS Scholarship — Kerala', 'slug': 'ews-kerala',
                'offering_organization': 'Kerala Social Welfare Department',
                'scholarship_type': 'COMMUNITY', 'eligible_communities': ["EWS"],
                'income_ceiling_annual': 800000, 'amount_per_year': 10000,
                'is_kerala_specific': True
            }
        ]

        created_count = 0
        for data in scholarships:
            obj, created = Scholarship.objects.get_or_create(
                slug=data['slug'],
                defaults=data
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} Scholarships.'))
