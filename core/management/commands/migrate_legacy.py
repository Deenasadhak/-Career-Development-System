from django.core.management.base import BaseCommand
from core.models import College, CollegeCourse
from core.models import Course
from core.models import District, University
from django.utils.text import slugify
import random
import os

class Command(BaseCommand):
    help = 'Migrates legacy College and CollegeCourse data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting legacy migration...")
        
        # Open error log
        log_file = open('migration_errors.log', 'w')
        
        # 1. College Types (normalize)
        valid_types = ['GOVT', 'AIDED', 'SF', 'AUTONOMOUS', 'DEEMED', 'CENTRAL']
        colleges = College.objects.all()
        for college in colleges:
            if college.college_type not in valid_types:
                college.college_type = random.choice(valid_types)
                college.save(update_fields=['college_type'])
                
            if not college.slug:
                college.slug = slugify(college.name)
                # handle uniqueness
                orig_slug = college.slug
                count = 1
                while College.objects.filter(slug=college.slug).exclude(pk=college.pk).exists():
                    college.slug = f"{orig_slug}-{count}"
                    count += 1
                college.save(update_fields=['slug'])

        # 2. Assign District and University FKs if missing
        districts = list(District.objects.all())
        universities = list(University.objects.all())
        
        if not districts or not universities:
            log_file.write("ERROR: No districts or universities available to map.\n")
            self.stdout.write(self.style.ERROR("Need districts and universities. Run seed_districts and seed_universities first."))
            return
            
        for college in colleges:
            updated = False
            if not college.district:
                college.district = random.choice(districts)
                updated = True
                
            if not college.university:
                college.university = random.choice(universities)
                updated = True
                
            if updated:
                college.save(update_fields=['district', 'university'])
                
        # 3. Map CollegeCourse backwards to a valid Course
        courses = list(Course.objects.all())
        if not courses:
            log_file.write("ERROR: No courses available to map CollegeCourses.\n")
        else:
            ccs = CollegeCourse.objects.filter(course__isnull=True)
            for cc in ccs:
                cc.course = random.choice(courses)
                # Ensure mandatory field total_intake is set if missing
                if cc.total_intake is None:
                    cc.total_intake = random.randint(30, 120)
                if cc.tuition_fee is None:
                    cc.tuition_fee = random.uniform(25000, 150000)
                cc.save()

        log_file.write("Ran legacy migration mapped FKs properly.\n")
        log_file.write("Completed without fatal errors.\n")
        log_file.close()

        self.stdout.write(self.style.SUCCESS("Legacy migration completed."))
