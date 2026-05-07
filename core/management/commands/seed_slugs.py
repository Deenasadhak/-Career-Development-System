from django.core.management.base import BaseCommand
from django.utils.text import slugify
from core.models import College
from core.models import Course

class Command(BaseCommand):
    help = 'Backfills slug fields for College and Course objects with empty slugs'

    def handle(self, *args, **kwargs):
        colleges_updated = 0
        courses_updated = 0

        # Update Colleges
        for college in College.objects.filter(slug=''):
            base = slugify(college.name)
            slug = base
            counter = 1
            while College.objects.filter(slug=slug).exclude(pk=college.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            college.slug = slug
            college.save(update_fields=['slug'])
            colleges_updated += 1
            self.stdout.write(self.style.SUCCESS(f'Updated slug for college: {college.name} -> {slug}'))

        # Update Courses
        for course in Course.objects.filter(slug=''):
            base = slugify(course.name)
            slug = base
            counter = 1
            # Special logic if course name is generic (e.g. B.Tech), it might collide heavily. 
            # But the logic requested is exactly basic counter loop.
            while Course.objects.filter(slug=slug).exclude(pk=course.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            course.slug = slug
            course.save(update_fields=['slug'])
            courses_updated += 1
            self.stdout.write(self.style.SUCCESS(f'Updated slug for course: {course.name} -> {slug}'))

        self.stdout.write(
            self.style.SUCCESS(f'Slugified {colleges_updated} colleges, {courses_updated} courses')
        )
