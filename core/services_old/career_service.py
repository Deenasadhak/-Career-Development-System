from django.db.models import Q
from core.models import Career, EntranceExam, Scholarship

class CareerService:

    def get_careers_for_student(self, student_profile, limit: int = 10) -> list[Career]:
        """
        Return careers most relevant to student:
        1. Filter Career.is_active = True
        2. Score each career:
           a) RIASEC match: get student's dominant RIASEC code
           b) Stream match: stream in student.interest_streams
           c) Demand bonus
           d) Gulf bonus (coastal districts)
        3. Order by score desc
        """
        careers = list(Career.objects.filter(is_active=True).prefetch_related(
            'qualifying_courses__discipline__field__stream'
        ))
        
        # Determine dominant RIASEC
        dominant_riasec = None
        session = getattr(student_profile, 'testsession_set', None)
        if session:
            latest_session = session.filter(status='COMPLETED').order_by('-completed_at').first()
            if latest_session and latest_session.riasec_scores:
                dominant_riasec = max(latest_session.riasec_scores, key=latest_session.riasec_scores.get)
        
        # Coastal districts for Gulf bonus
        coastal = ['Thiruvananthapuram', 'Kollam', 'Alappuzha', 'Ernakulam', 'Thrissur', 'Malappuram', 'Kozhikode', 'Kannur', 'Kasaragod']
        is_coastal = student_profile.district and student_profile.district.name in coastal

        student_streams = set(student_profile.interest_streams.values_list('id', flat=True))

        scored_careers = []
        for career in careers:
            score = 0
            
            # RIASEC
            if dominant_riasec:
                if career.riasec_primary == dominant_riasec:
                    score += 50
                elif career.riasec_secondary == dominant_riasec:
                    score += 25
                    
            # Stream match
            stream_match = False
            for qc in career.qualifying_courses.all():
                if qc.discipline and qc.discipline.field and qc.discipline.field.stream_id in student_streams:
                    stream_match = True
                    break
            if stream_match:
                score += 30
                
            # Demand bonus
            if career.job_demand == 'HIGH':
                score += 20
            elif career.job_demand == 'MEDIUM':
                score += 10
                
            # Gulf bonus
            if career.gulf_opportunity and is_coastal:
                score += 15
                
            scored_careers.append((score, career))
            
        scored_careers.sort(key=lambda x: x[0], reverse=True)
        return [c for s, c in scored_careers[:limit]]

    def get_eligible_scholarships(self, student_profile) -> list[Scholarship]:
        """
        Filter and return eligible scholarships.
        """
        qs = Scholarship.objects.filter(is_active=True)
        
        if not student_profile.is_pwd:
            qs = qs.exclude(is_pwd_only=True)
            
        if student_profile.gender != 'F':
            qs = qs.exclude(is_girl_only=True)
            
        if student_profile.annual_family_income is not None:
            qs = qs.exclude(income_ceiling_annual__lt=student_profile.annual_family_income)
            
        eligible = []
        for scholarship in qs:
            if scholarship.is_eligible_for(student_profile):
                eligible.append(scholarship)
                
        eligible.sort(key=lambda x: x.amount_per_year, reverse=True)
        return eligible

    def get_career_path(self, career: Career) -> dict:
        """
        Return structured career progression dict.
        """
        return {
          "career_title": career.title,
          "minimum_qualification": career.minimum_qualification,
          "progression": [
            {
              "stage": "Entry Level",
              "roles": career.entry_roles,
              "typical_years": "0-2",
            },
            {
              "stage": "Mid Level",
              "roles": career.mid_roles,
              "typical_years": "2-5",
            },
            {
              "stage": "Senior Level",
              "roles": career.senior_roles,
              "typical_years": "5+",
            },
          ],
          "timeline": career.progression_timeline,
          "kerala_context": career.kerala_job_market_notes,
          "gulf_opportunity": {
            "available": career.gulf_opportunity,
            "notes": career.gulf_notes,
          },
          "salary_growth": {
            "entry": f"₹{career.salary_kerala_min}L - ₹{career.salary_kerala_min * 1.5:.1f}L LPA",
            "kerala_range": career.salary_range_kerala,
            "india_avg": f"₹{career.salary_india_avg}L",
            "abroad_avg": f"₹{career.salary_abroad_avg}L" if career.salary_abroad_avg else "N/A",
          },
          "top_employers": {
            "kerala": career.top_employers_kerala,
            "india": career.top_employers_india,
            "abroad": career.top_employers_abroad,
          },
          "skills_needed": {
            "technical": career.technical_skills,
            "soft": career.soft_skills,
          },
          "related_careers": [
            {"title": c.title, "slug": c.slug}
            for c in career.related_careers.all()[:4]
          ],
        }

    def get_exam_calendar(self) -> list[dict]:
        """
        Return all active EntranceExam ordered by exam_month.
        Month ordering: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec, Unknown
        """
        month_order = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        
        exams = EntranceExam.objects.filter(is_active=True).prefetch_related('courses_unlocked')
        
        calendar = []
        for exam in exams:
            month_str = exam.exam_month
            order_idx = month_order.get(month_str, 99)
            calendar.append({
                'exam': exam,
                'month': month_str,
                'is_kerala': exam.is_kerala_specific,
                'courses_count': exam.courses_unlocked.count(),
                '_order': order_idx
            })
            
        calendar.sort(key=lambda x: x['_order'])
        
        for item in calendar:
            del item['_order']
            
        return calendar

    def get_exams_for_course(self, course) -> list[EntranceExam]:
        """
        Return all active entrance exams that unlock the given course,
        ordered by level (STATE before NATIONAL before UNIVERSITY).
        """
        level_order = {'STATE': 1, 'NATIONAL': 2, 'UNIVERSITY': 3}
        exams = list(course.unlocked_by_exams.filter(is_active=True))
        exams.sort(key=lambda x: level_order.get(x.level, 99))
        return exams
