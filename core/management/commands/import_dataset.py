import pandas as pd
from django.core.management.base import BaseCommand
from core.models import College, Course, CollegeCourse, CareerPath, KeralaReference
import os

class Command(BaseCommand):
    help = 'Imports Kerala College Dataset from Excel with fixed header detection and mapping'

    def handle(self, *args, **kwargs):
        file_path = r'C:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project\Dataset\Kerala_College_Dataset.xlsx'
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        self.stdout.write("Reading Excel file...")
        excel = pd.ExcelFile(file_path)

        def get_df(sheet_name):
            # Read everything first to find the real header
            df_full = excel.parse(sheet_name, header=None)
            header_idx = 0
            for i, row in df_full.iterrows():
                # Convert row to list of strings, stripping spaces
                row_vals = [str(x).strip() for x in row.values if pd.notnull(x)]
                # Header row usually has many non-empty values and contains keywords
                if len(row_vals) >= 3 and any(k in " ".join(row_vals) for k in ['ID', 'Name', 'District', 'Course', 'College', 'Cutoff']):
                    # Check if it's not a title row (title rows often have data in only first column)
                    if not (len(row_vals) == 1 and i == 0):
                        header_idx = i
                        break
            
            df = excel.parse(sheet_name, header=header_idx)
            # Clean column names
            df.columns = [str(c).strip() for c in df.columns]
            # Clean data cells (strip strings)
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            return df

        # 1. Import Colleges
        self.stdout.write("Importing Colleges...")
        df_colleges = get_df('Colleges')
        for _, row in df_colleges.iterrows():
            cid = str(row.get('College ID', '')).strip()
            if not cid or cid == 'nan': continue
            
            College.objects.update_or_create(
                college_id=cid,
                defaults={
                    'name': row.get('College Name'),
                    'district': row.get('District'),
                    'city': row.get('City/Town', ''),
                    'university': row.get('University Affiliation', ''),
                    'college_type': row.get('College Type', ''),
                    'naac_grade': row.get('NAAC Grade', ''),
                    'nirf_state_rank': int(row['NIRF Ranking (State)']) if pd.notnull(row.get('NIRF Ranking (State)')) else None,
                    'total_seats': int(row['Total Seats']) if pd.notnull(row.get('Total Seats')) else 0,
                    'hostel_available': str(row.get('Hostel Available', '')).lower() == 'yes',
                    'website': str(row.get('Website', '')),
                    'contact_email': str(row.get('Contact Email', '')),
                }
            )

        # 2. Import Courses
        self.stdout.write("Importing Courses...")
        df_courses = get_df('Courses')
        for _, row in df_courses.iterrows():
            crs_id = str(row.get('Course ID', '')).strip()
            if not crs_id or crs_id == 'nan': continue
            
            Course.objects.update_or_create(
                course_id=crs_id,
                defaults={
                    'name': row.get('Course Name'),
                    'degree_type': row.get('Degree Type', ''),
                    'stream': row.get('Stream', ''),
                    'discipline': row.get('Category', ''),
                    'duration_years': float(row['Duration (Yrs)']) if pd.notnull(row.get('Duration (Yrs)')) else 3.0,
                    'min_percentage': int(row['Min % Required']) if pd.notnull(row.get('Min % Required')) else 45,
                    'eligible_streams': str(row.get('Eligible 12th Streams', '')),
                    'cap_applicable': str(row.get('CAP Applicable', '')).lower() == 'yes',
                    'kerala_demand_score': int(row['Kerala Demand Score (1-100)']) if pd.notnull(row.get('Kerala Demand Score (1-100)')) else 50,
                    'avg_salary_kerala': str(row.get('Avg Salary Kerala (INR/yr)', '')),
                }
            )

        # 3. Import College_Course_Cutoffs
        self.stdout.write("Importing College-Course mappings...")
        df_cc = get_df('College_Course_Cutoffs')
        mappings_count = 0
        for _, row in df_cc.iterrows():
            cid = str(row.get('College ID', '')).strip()
            crs_id = str(row.get('Course ID', '')).strip()
            if not cid or cid == 'nan' or not crs_id or crs_id == 'nan': continue
            
            college = College.objects.filter(college_id=cid).first()
            course = Course.objects.filter(course_id=crs_id).first()
            
            if college and course:
                CollegeCourse.objects.update_or_create(
                    college=college,
                    course=course,
                    defaults={
                        'fee_per_year': str(row.get('Fee/Year (INR)', '0')),
                        'total_intake': int(row['Total Seats']) if pd.notnull(row.get('Total Seats')) else 0,
                        'govt_quota_seats': int(row['Govt Quota Seats']) if pd.notnull(row.get('Govt Quota Seats')) else 0,
                        'mgmt_quota_seats': int(row['Mgmt Quota Seats']) if pd.notnull(row.get('Mgmt Quota Seats')) else 0,
                        'cutoff_general': int(row['Cutoff Mark (out of 600)']) if pd.notnull(row.get('Cutoff Mark (out of 600)')) else 0,
                    }
                )
                mappings_count += 1
            else:
                if not college: self.stdout.write(self.style.WARNING(f"College ID {cid} not found for mapping"))
                if not course: self.stdout.write(self.style.WARNING(f"Course ID {crs_id} not found for mapping"))

        self.stdout.write(f"Total mappings created: {mappings_count}")

        # 4. Import Career_Paths
        self.stdout.write("Importing Career Paths...")
        df_careers = get_df('Career_Paths')
        for _, row in df_careers.iterrows():
            crs_id = str(row.get('Course ID', '')).strip()
            if not crs_id or crs_id == 'nan': continue
            
            course = Course.objects.filter(course_id=crs_id).first()
            if course:
                CareerPath.objects.update_or_create(
                    course=course,
                    career_path_name=row['Career Path'],
                    defaults={
                        'top_job_roles': row.get('Top Job Roles in Kerala', ''),
                        'avg_salary_kerala': str(row.get('Avg Salary Kerala (INR/yr)', '')),
                        'gulf_opportunity': str(row.get('Gulf Opportunity', '')),
                        'top_employers': str(row.get('Top Employers', '')),
                        'further_studies': str(row.get('Further Studies', '')),
                        'demand_score': int(row['Demand Score']) if pd.notnull(row.get('Demand Score')) else 0,
                        'psc_exam_relevant': str(row.get('Key PSC Exams Applicable', '')),
                    }
                )
                course.top_job_roles = row.get('Top Job Roles in Kerala', '')
                course.save()

        # 5. Import Kerala_Reference
        self.stdout.write("Importing Kerala Reference data...")
        df_ref = get_df('Kerala_Reference')
        for _, row in df_ref.iterrows():
            district = str(row.get('District', '')).strip()
            if not district or district == 'nan': continue
            
            KeralaReference.objects.update_or_create(
                district=district,
                defaults={
                    'region': row.get('Region', ''),
                    'university_affiliation': row.get('University Affiliation', ''),
                    'cap_nodal_center': row.get('CAP Nodal Center', ''),
                    'cap_helpline': str(row.get('CAP Helpline', '')),
                    'govt_quota_percent': int(row['Govt Quota %']) if pd.notnull(row.get('Govt Quota %')) else 75,
                    'mgmt_quota_percent': int(row['Management Quota %']) if pd.notnull(row.get('Management Quota %')) else 25,
                    'psc_exams': str(row.get('Key PSC Exams Applicable', '')),
                }
            )

        self.stdout.write(self.style.SUCCESS("Successfully imported all data!"))
