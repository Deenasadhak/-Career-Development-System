from django.core.management.base import BaseCommand
from core.models import EntranceExam
from core.models import Course

class Command(BaseCommand):
    help = 'Seed Entrance Exams'

    def handle(self, *args, **options):
        exams = [
            # Kerala
            {
                'name': 'Kerala Engineering Architecture Medicine', 'short_name': 'KEAM',
                'conducting_body': 'Commissioner for Entrance Examinations (CEE) Kerala',
                'level': 'STATE', 'description': 'State level entrance for engineering and medical allied courses.',
                'eligibility': 'Plus Two with PCM/PCB.',
                'exam_pattern': {"subjects": ["Physics","Chemistry","Maths"], "total_marks": 300, "duration_hours": 2.5, "negative_marking": True},
                'notification_month': 'January', 'exam_month': 'April', 'result_month': 'June',
                'is_kerala_specific': True
            },
            {
                'name': 'Kerala Management Aptitude Test', 'short_name': 'KMAT Kerala',
                'conducting_body': 'KUFOS / CUSAT',
                'level': 'STATE', 'description': 'State level MBA entrance.',
                'eligibility': 'Graduation with 50% marks.',
                'exam_pattern': {"total_marks": 720, "questions": 180, "sections": 4},
                'notification_month': 'June', 'exam_month': 'August', 'result_month': 'September',
                'is_kerala_specific': True
            },
            {
                'name': 'Kerala State Eligibility Test', 'short_name': 'Kerala SET',
                'conducting_body': 'LBS Centre for Science and Technology',
                'level': 'STATE', 'description': 'Mandatory for Higher Secondary School Teachers in Kerala.',
                'eligibility': 'Master degree with B.Ed.',
                'exam_pattern': {"papers": 2},
                'notification_month': 'September', 'exam_month': 'December', 'result_month': 'January',
                'is_kerala_specific': True
            },
            # National
            {
                'name': 'National Eligibility cum Entrance Test (Undergraduate)', 'short_name': 'NEET-UG',
                'conducting_body': 'NTA',
                'level': 'NATIONAL', 'description': 'National medical entrance exam.',
                'eligibility': 'Plus Two with PCB.',
                'exam_pattern': {"Physics":180,"Chemistry":180,"Biology":360,"total_marks": 720, "duration_hours": 3.33, "negative_marking": True},
                'is_kerala_specific': False
            },
            {
                'name': 'Joint Entrance Examination (Main)', 'short_name': 'JEE Main',
                'conducting_body': 'NTA',
                'level': 'NATIONAL', 'description': 'National engineering entrance exam.',
                'eligibility': 'Plus Two with PCM.',
                'exam_pattern': {"Physics":100,"Chemistry":100,"Maths":100,"total_marks": 300, "duration_hours": 3},
                'is_kerala_specific': False
            },
            {
                'name': 'Joint Entrance Examination (Advanced)', 'short_name': 'JEE Advanced',
                'conducting_body': 'IITs',
                'level': 'NATIONAL', 'description': 'IIT admission exam.',
                'eligibility': 'JEE Main top 2.5 lakh.',
                'exam_pattern': {"papers": 2},
                'is_kerala_specific': False
            },
            {
                'name': 'Common Law Admission Test', 'short_name': 'CLAT',
                'conducting_body': 'Consortium of NLUs',
                'level': 'NATIONAL', 'description': 'Law entrance exam.',
                'eligibility': 'Plus Two with 45%.',
                'exam_pattern': {"English":20,"GK":25,"Legal":25,"Logical":20,"Quant":10, "total_questions": 120, "duration_hours": 2},
                'is_kerala_specific': False
            },
            {
                'name': 'Common Admission Test', 'short_name': 'CAT',
                'conducting_body': 'IIMs',
                'level': 'NATIONAL', 'description': 'MBA entrance exam.',
                'eligibility': 'Graduation with 50%.',
                'exam_pattern': {"VARC":24,"DILR":20,"QA":22, "total_questions": 66, "duration_mins": 120},
                'is_kerala_specific': False
            },
            {
                'name': 'Common University Entrance Test', 'short_name': 'CUET',
                'conducting_body': 'NTA',
                'level': 'NATIONAL', 'description': 'Central university entrance exam.',
                'eligibility': 'Plus Two passing grade.',
                'exam_pattern': {"sections": 3},
                'is_kerala_specific': False
            }
        ]

        created_count = 0
        for data in exams:
            obj, created = EntranceExam.objects.get_or_create(
                short_name=data['short_name'],
                defaults=data
            )
            if created:
                created_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} Entrance Exams.'))
