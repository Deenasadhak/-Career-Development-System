from django.core.management.base import BaseCommand
from core.models import District

class Command(BaseCommand):
    help = 'Seeds 14 Kerala districts'

    def handle(self, *args, **kwargs):
        districts = [
            ("Thiruvananthapuram", "SOUTH"),
            ("Kollam", "SOUTH"),
            ("Pathanamthitta", "SOUTH"),
            ("Alappuzha", "SOUTH"),
            ("Kottayam", "SOUTH"),
            ("Idukki", "CENTRAL"),
            ("Ernakulam", "CENTRAL"),
            ("Thrissur", "CENTRAL"),
            ("Palakkad", "CENTRAL"),
            ("Malappuram", "NORTH"),
            ("Kozhikode", "NORTH"),
            ("Wayanad", "NORTH"),
            ("Kannur", "NORTH"),
            ("Kasaragod", "NORTH"),
        ]
        
        for name, region in districts:
            District.objects.get_or_create(
                name=name,
                defaults={
                    'region': region,
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(districts)} districts."))
