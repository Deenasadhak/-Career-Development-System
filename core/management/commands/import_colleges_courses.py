import pandas as pd
import os
from django.core.management.base import BaseCommand
from core.models import College, Course, CollegeCourse
from django.db import transaction

class Command(BaseCommand):
    help = 'Import colleges and courses from Kerala_Colleges_and_Courses.xlsx'

    def handle(self, *args, **options):
        file_path = r'c:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project\Dataset\Kerala_Colleges_and_Courses.xlsx'
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found at {file_path}'))
            return

        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading Excel: {e}'))
            return

        # Data starts from row 1 (index 0 is header row from Excel view, but pandas might have read it as data if not specified)
        # Looking at previous inspect, headers were Unnamed: 1 etc.
        # Let's read it properly by skipping the first row if it's just headers.
        # Based on inspect: Row 0 is index 0 in dataframe.
        
        # Mapping:
        # col 1 (index 1): College Name
        # col 2 (index 2): District
        # col 3-7 (index 3-7): Courses
        
        clg_count = 0
        crs_count = 0
        mapping_count = 0
        
        # Get starting IDs
        last_clg = College.objects.all().order_by('college_id').last()
        last_clg_id = int(last_clg.college_id.replace('COL', '')) if last_clg and last_clg.college_id and last_clg.college_id.startswith('COL') else 40
        
        last_crs = Course.objects.all().order_by('course_id').last()
        last_crs_id = int(last_crs.course_id.replace('CRS', '')) if last_crs and last_crs.course_id and last_crs.course_id.startswith('CRS') else 35

        with transaction.atomic():
            for index, row in df.iterrows():
                if index == 0: # Header row in the file as read by pandas
                    continue
                
                clg_name = str(row.iloc[1]).strip()
                district = str(row.iloc[2]).strip()
                
                if not clg_name or clg_name == 'nan':
                    continue
                
                # Find or create college
                college = College.objects.filter(name__iexact=clg_name).first()
                if not college:
                    last_clg_id += 1
                    college = College.objects.create(
                        name=clg_name,
                        district=district if district != 'nan' else 'Unknown',
                        college_id=f'COL{last_clg_id:03d}'
                    )
                    clg_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Created College: {clg_name}'))
                
                # Iterate through courses
                for i in range(3, 8):
                    crs_name = str(row.iloc[i]).strip()
                    if not crs_name or crs_name == 'nan':
                        continue
                    
                    # Find or create course
                    course = Course.objects.filter(name__iexact=crs_name).first()
                    if not course:
                        last_crs_id += 1
                        
                        # Infer stream
                        stream = 'Science'
                        if any(x in crs_name.upper() for x in ['B.COM', 'BBA', 'COMMERCE']):
                            stream = 'Commerce'
                        elif any(x in crs_name.upper() for x in ['BA ', 'ARTS', 'ECONOMICS', 'HISTORY', 'ENGLISH']):
                            stream = 'Arts'
                        
                        course = Course.objects.create(
                            name=crs_name,
                            course_id=f'CRS{last_crs_id:03d}',
                            stream=stream,
                            degree_type='UG' if crs_name.upper().startswith('B') else 'PG'
                        )
                        crs_count += 1
                        self.stdout.write(self.style.SUCCESS(f'Created Course: {crs_name}'))
                    
                    # Create mapping
                    mapping, created = CollegeCourse.objects.get_or_create(
                        college=college,
                        course=course
                    )
                    if created:
                        mapping_count += 1
            
        self.stdout.write(self.style.SUCCESS(f'Import completed!'))
        self.stdout.write(self.style.SUCCESS(f'New Colleges: {clg_count}'))
        self.stdout.write(self.style.SUCCESS(f'New Courses: {crs_count}'))
        self.stdout.write(self.style.SUCCESS(f'New Mappings: {mapping_count}'))
