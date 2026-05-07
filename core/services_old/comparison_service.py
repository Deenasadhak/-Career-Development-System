from core.models import College, CollegeCourse, CollegeCourseYearlyCutoff
from core.models import Course

class ComparisonService:

    MAX_COLLEGES = 4
    MAX_COURSES = 3

    def compare_colleges(self, college_ids: list[int], course_id: int) -> dict:
        if not (2 <= len(college_ids) <= self.MAX_COLLEGES):
            raise ValueError(f"Can only compare between 2 and {self.MAX_COLLEGES} colleges.")

        course = Course.objects.select_related('discipline__field__stream').get(id=course_id)
        
        colleges = College.objects.filter(id__in=college_ids).select_related('district', 'university')
        
        college_courses = CollegeCourse.objects.filter(
            college_id__in=college_ids, course_id=course_id
        ).prefetch_related('yearly_cutoffs')
        
        cc_map = {cc.college_id: cc for cc in college_courses}

        result_colleges = []
        lowest_fee = float('inf')
        lowest_fee_college = ""
        
        highest_placement = -1.0
        highest_placement_college = ""

        best_naac_rank = 999
        best_naac_college = ""

        lowest_cutoff = float('inf')
        lowest_cutoff_college = ""

        for college in colleges:
            cc = cc_map.get(college.id)
            
            tuition = cc.tuition_fee if cc else None
            hostel = cc.hostel_fee if cc else None
            transport = cc.transport_fee if cc else None
            total_estimated = None
            if cc:
                total_estimated = sum(filter(None, [tuition, hostel, transport]))
            
            if total_estimated is not None and total_estimated < lowest_fee:
                lowest_fee = total_estimated
                lowest_fee_college = college.name
                
            naac_rank = self.get_naac_rank(college.naac_grade)
            if naac_rank < best_naac_rank:
                best_naac_rank = naac_rank
                best_naac_college = college.name

            history = []
            curr_gen = curr_sc = curr_st = curr_obc = None
            if cc:
                cutoffs = list(cc.yearly_cutoffs.order_by('-year')[:3])
                for cto in cutoffs:
                    history.append({
                        "year": cto.year,
                        "general": cto.general_cutoff,
                        "sc": cto.sc_cutoff,
                        "st": cto.st_cutoff
                    })
                curr_gen = cc.cutoff_general
                curr_sc = cc.cutoff_sc
                curr_st = cc.cutoff_st
                curr_obc = cc.cutoff_obc
                
                if curr_gen is not None and curr_gen < lowest_cutoff:
                    lowest_cutoff = curr_gen
                    lowest_cutoff_college = college.name
            
            placement_pct = cc.placement_percentage if cc else None
            if placement_pct is not None and placement_pct > highest_placement:
                highest_placement = placement_pct
                highest_placement_college = college.name

            result_colleges.append({
                "id": college.id,
                "name": college.name,
                "short_name": college.short_name,
                "college_type": college.college_type,
                "college_type_display": college.get_college_type_display(),
                "naac_grade": college.naac_grade,
                "nirf_rank": college.nirf_rank,
                "established_year": college.established_year,
                "district": college.district.name if college.district else "",
                "university": college.university.name if college.university else "",
                "website": college.website,
                "course_offered": cc is not None,
                "fees": {
                    "tuition": tuition,
                    "hostel": hostel,
                    "transport": transport,
                    "total_estimated": total_estimated,
                },
                "intake": {
                    "total": cc.total_seats if cc else None,
                    "govt_quota": cc.govt_seats if cc else None,
                    "management_quota": cc.management_seats if cc else None,
                },
                "cutoffs": {
                    "current_general": curr_gen,
                    "current_sc": curr_sc,
                    "current_st": curr_st,
                    "current_obc": curr_obc,
                    "history": history,
                },
                "placement": {
                    "percentage": placement_pct,
                    "avg_package_lpa": cc.average_package if cc else None,
                    "highest_package_lpa": cc.highest_package if cc else None,
                    "top_recruiters": cc.top_recruiters if cc else [],
                },
                "facilities": {
                    "hostel_boys": college.has_hostel_boys,
                    "hostel_girls": college.has_hostel_girls,
                    "transport": college.has_transport,
                    "wifi": college.has_wifi,
                    "library": college.has_library,
                    "sports": college.has_sports,
                    "placement_cell": college.has_placement_cell,
                    "medical": college.has_medical,
                },
                "admission_mode": cc.admission_mode if cc else None,
                "medium": cc.medium if cc else None,
                "lateral_entry": cc.lateral_entry if cc else False,
            })

        return {
            "course": {
                "id": course.id,
                "name": course.name,
                "level": course.get_level_display(),
                "duration_years": course.duration_years,
                "discipline": course.discipline.name if course.discipline else "",
                "stream": course.discipline.field.stream.name if course.discipline and course.discipline.field else "",
            },
            "colleges": result_colleges,
            "comparison_highlights": {
                "lowest_fee_college": lowest_fee_college,
                "highest_placement_college": highest_placement_college,
                "best_naac_college": best_naac_college,
                "lowest_cutoff_college": lowest_cutoff_college,
            }
        }

    def compare_courses(self, college_course_ids: list[int]) -> dict:
        if not (2 <= len(college_course_ids) <= self.MAX_COURSES):
            raise ValueError(f"Can only compare between 2 and {self.MAX_COURSES} courses.")
            
        ccs = list(CollegeCourse.objects.filter(id__in=college_course_ids).select_related(
            'college__district',
            'course__discipline__field__stream',
            'specialization'
        ).prefetch_related('course__unlocked_by_exams', 'course__career_outcomes'))
        
        items = []
        lowest_fee = float('inf')
        lowest_fee_course = ""
        
        best_placement = -1.0
        best_placement_course = ""
        
        shortest_duration = float('inf')
        shortest_duration_course = ""

        for cc in ccs:
            tuition = cc.tuition_fee or 0
            hostel = cc.hostel_fee or 0
            transport = cc.transport_fee or 0
            total_fee = sum(filter(None, [tuition, hostel, transport]))
            
            if total_fee < lowest_fee:
                lowest_fee = total_fee
                lowest_fee_course = cc.course.name
                
            placement = cc.placement_percentage
            if placement is not None and placement > best_placement:
                best_placement = placement
                best_placement_course = cc.course.name
                
            duration = cc.course.duration_years
            if duration is not None and duration < shortest_duration:
                shortest_duration = duration
                shortest_duration_course = cc.course.name

            exams = [{"name": ex.name, "short_name": ex.short_name} for ex in cc.course.unlocked_by_exams.all()]
            careers = [{"title": cr.title, "slug": cr.slug} for cr in cc.course.career_outcomes.all()[:4]]

            items.append({
                "college_course_id": cc.id,
                "college_name": cc.college.name,
                "college_type": cc.college.college_type,
                "naac_grade": cc.college.naac_grade,
                "district": cc.college.district.name if cc.college.district else "",
                "course_name": cc.course.name,
                "stream": cc.course.discipline.field.stream.name if cc.course.discipline and cc.course.discipline.field else "",
                "discipline": cc.course.discipline.name if cc.course.discipline else "",
                "level": cc.course.get_level_display(),
                "duration_years": cc.course.duration_years,
                "specialization": cc.specialization.name if cc.specialization else None,
                "tuition_fee": cc.tuition_fee,
                "total_estimated_fee": total_fee,
                "cutoff_general": cc.cutoff_general,
                "placement_percentage": cc.placement_percentage,
                "avg_package_lpa": cc.average_package,
                "admission_mode": cc.admission_mode,
                "medium": cc.medium,
                "lateral_entry": cc.lateral_entry,
                "entrance_exams_required": exams,
                "career_outcomes": careers,
            })
            
        return {
            "items": items,
            "comparison_highlights": {
                "lowest_fee": lowest_fee_course,
                "best_placement": best_placement_course,
                "shortest_duration": shortest_duration_course,
            }
        }

    def get_naac_rank(self, grade: str) -> int:
        ranks = {
            'A++': 1, 'A+': 2, 'A': 3, 'B++': 4, 'B+': 5,
            'B': 6, 'C': 7, 'PENDING': 8, 'NA': 9
        }
        return ranks.get(grade, 9)
