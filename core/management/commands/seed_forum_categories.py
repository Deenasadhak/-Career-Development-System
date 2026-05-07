from django.core.management.base import BaseCommand
from core.models import ForumCategory

class Command(BaseCommand):
    help = 'Seeds forum categories'

    def handle(self, *args, **kwargs):
        categories = [
            ("Admissions & Counselling", "admissions", "#3B82F6", 1, "Questions about college admissions, CAP process, and counselling"),
            ("Engineering & Technology", "engineering", "#6366F1", 2, "Discussions about engineering courses and careers"),
            ("Medical & Health Sciences", "medical", "#EF4444", 3, "Medical, Dental, and Healthcare related queries"),
            ("Commerce & Management", "commerce", "#10B981", 4, "CA, MBA, and business studies"),
            ("Arts & Humanities", "arts", "#F59E0B", 5, "Literature, social sciences, and fine arts"),
            ("Kerala PSC & Government Jobs", "psc-jobs", "#8B5CF6", 6, "Kerala PSC exam preparation, government job opportunities"),
            ("Gulf Careers & Abroad", "gulf-careers", "#0EA5E9", 7, "Opportunities in Middle East and overseas education"),
            ("Scholarships & Financial Aid", "scholarships", "#84CC16", 8, "Funding your education"),
            ("College Life & Reviews", "college-life", "#F97316", 9, "Student experiences, college reviews, hostel life"),
            ("General Discussion", "general", "#6B7280", 10, "Anything else relevant to career development")
        ]

        for name, slug, color, order, desc in categories:
            cat, created = ForumCategory.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'color_code': color,
                    'order': order,
                    'description': desc
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {name}"))
            else:
                self.stdout.write(f"Category already exists: {name}")
        
        self.stdout.write(self.style.SUCCESS("Forum categories seeded successfully!"))
