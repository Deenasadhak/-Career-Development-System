from django.core.management.base import BaseCommand
from core.models import University

class Command(BaseCommand):
    help = 'Seeds major Universities in Kerala'

    def handle(self, *args, **kwargs):
        universities = [
            ("University of Kerala", "KU", "STATE"),
            ("Mahatma Gandhi University", "MGU", "STATE"),
            ("University of Calicut", "CU", "STATE"),
            ("Kannur University", "KNU", "STATE"),
            ("Cochin University of Science and Technology", "CUSAT", "STATE"),
            ("APJ Abdul Kalam Technological University", "KTU", "STATE"),
            ("Kerala University of Health Sciences", "KUHS", "STATE"),
            ("Kerala Veterinary and Animal Sciences University", "KVASU", "STATE"),
            ("Kerala University of Fisheries and Ocean Studies", "KUFOS", "STATE"),
            ("National University of Advanced Legal Studies", "NUALS", "STATE"),
            ("Thunchath Ezhuthachan Malayalam University", "TEMU", "STATE"),
            ("Sree Sankaracharya University of Sanskrit", "SSUS", "STATE"),
        ]
        
        for name, short_name, u_type in universities:
            University.objects.get_or_create(
                name=name,
                defaults={
                    'short_name': short_name,
                    'university_type': u_type,
                }
            )
            
        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(universities)} universities."))
