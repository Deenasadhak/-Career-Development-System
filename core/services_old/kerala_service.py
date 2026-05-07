from django.apps import apps
from django.db.models import Count, Q
from django.utils import timezone
from core.models import CAPRound, PSCPost, GulfCareerOpportunity, GulfCountry
from core.models import Course
from core.models import Career
from core.models import District

COASTAL_DISTRICTS = [
    'Thiruvananthapuram', 'Kollam', 'Alappuzha',
    'Ernakulam', 'Thrissur', 'Malappuram',
    'Kozhikode', 'Kannur', 'Kasaragod',
]

class KeralaService:

    def get_cap_guidance(self, student_profile) -> dict:
        StudentRecommendation = apps.get_model('core', 'StudentRecommendation')
        
        recs = StudentRecommendation.objects.filter(
            student=student_profile,
            eligibility_status__in=['ELIGIBLE', 'BORDERLINE']
        ).select_related('college_course__college', 'college_course__course').order_by('-total_score')[:15]
        
        current_year_str = str(timezone.now().year)
        # Using icontains to match 2024 in "2024-2025" or similar
        cap_rounds = list(CAPRound.objects.filter(is_active=True, academic_year__icontains=current_year_str).order_by('round_number'))
        
        option_list = []
        total_cap_options = 0
        total_management_options = 0
        
        for rank, rec in enumerate(recs, start=1):
            cc = rec.college_course
            is_cap = cc.admission_mode == 'CAP'
            is_management = not is_cap
            
            if is_cap:
                total_cap_options += 1
            else:
                total_management_options += 1
                
            strategy_note = ""
            if rec.eligibility_status == 'ELIGIBLE':
                strategy_note = f"Place this as option {total_cap_options} — you have a strong chance based on your marks vs last year cutoff." if is_cap else f"Strong chance for Management strictly. Contact college quickly."
            else:
                strategy_note = f"Borderline chance. Keep as a backup or later option."
                
            option_list.append({
                "rank": rank,
                "college_name": cc.college.name,
                "course_name": cc.course.name,
                "district": cc.college.district.name if cc.college.district else "",
                "cutoff_general": cc.cutoff_general,
                "your_percentage": student_profile.plus_two_percentage,
                "admission_chance": rec.get_eligibility_status_display(),
                "is_cap": is_cap,
                "is_management": is_management,
                "tuition_fee": cc.tuition_fee or 0.0,
                "recommendation_score": rec.total_score,
                "strategy_note": strategy_note,
            })
            
        # Strategy summary
        has_eligible = any(r.eligibility_status == 'ELIGIBLE' for r in recs)
        eligible_count = sum(1 for r in recs if r.eligibility_status == 'ELIGIBLE')
        
        summary = ""
        has_eng = student_profile.interest_streams.filter(slug='engineering-technology').exists()
        has_med = student_profile.interest_streams.filter(slug='medicine-healthcare').exists()
        
        if student_profile.keam_rank and has_eng:
            summary += "Your KEAM rank makes you eligible for Kerala Engineering Architecture Medical (KEAM) CAP process. Ensure you register on the CEE Kerala portal. "
        if student_profile.neet_score and has_med:
            summary += "Your NEET score applies to the Kerala Medical allotment. Follow CEE guidelines for state quota. "
            
        if eligible_count >= 3:
            summary += "You have strong options. Prioritize government colleges in your preferred district for lower fees. "
        elif eligible_count == 0:
            summary += "Consider management quota or improving marks. Here are your best borderline options. "
            
        summary += f"There are generally {len(cap_rounds)} CAP rounds. It is critical to report to the college on time once allotted."
        
        important_dates = []
        for r in cap_rounds:
            if r.registration_start:
                important_dates.append({"round": r.round_number, "event": "Registration Starts", "date": r.registration_start})
            if r.registration_end:
                important_dates.append({"round": r.round_number, "event": "Registration Ends", "date": r.registration_end})
            if r.allotment_date:
                important_dates.append({"round": r.round_number, "event": "Allotment Publication", "date": r.allotment_date})
            if r.fee_payment_deadline:
                important_dates.append({"round": r.round_number, "event": "Fee Deadline", "date": r.fee_payment_deadline})
            if r.reporting_start:
                important_dates.append({"round": r.round_number, "event": "Reporting Starts", "date": r.reporting_start})
            if r.reporting_end:
                important_dates.append({"round": r.round_number, "event": "Reporting Ends", "date": r.reporting_end})

        # Sort dates
        important_dates.sort(key=lambda x: x['date'])
            
        return {
            "option_list": option_list,
            "cap_rounds": cap_rounds,
            "strategy_summary": summary.strip(),
            "total_cap_options": total_cap_options,
            "total_management_options": total_management_options,
            "important_dates": important_dates,
        }

    def get_psc_opportunities(self, student_profile) -> list[PSCPost]:
        streams = student_profile.interest_streams.all()
        
        qs = PSCPost.objects.filter(is_active=True).filter(
            Q(required_courses__discipline__field__stream__in=streams) |
            Q(related_careers__is_psc_available=True, related_careers__qualifying_courses__discipline__field__stream__in=streams)
        ).select_related('department').prefetch_related(
            'required_courses', 'related_careers'
        ).distinct().order_by('department__name', 'title')
        
        return list(qs)

    def get_gulf_opportunities(self, student_profile=None) -> dict:
        qs = GulfCareerOpportunity.objects.filter(is_active=True).select_related('career', 'country')
        
        if student_profile:
            streams = student_profile.interest_streams.all()
            qs = qs.filter(career__qualifying_courses__discipline__field__stream__in=streams).distinct()
            
        by_country = {}
        by_career = {}
        all_opps = list(qs)
        
        for opp in all_opps:
            c_name = opp.country.name
            if c_name not in by_country:
                by_country[c_name] = {
                    "country": opp.country,
                    "opportunities": [],
                    "total_count": 0,
                }
            by_country[c_name]["opportunities"].append(opp)
            by_country[c_name]["total_count"] += 1
            
            career_t = opp.career.title
            if career_t not in by_career:
                by_career[career_t] = []
            by_career[career_t].append(opp)
            
        top_opps = sorted(all_opps, key=lambda x: x.avg_salary_inr_lpa, reverse=True)[:5]
        
        is_coastal = False
        if student_profile and student_profile.district:
            is_coastal = self.is_coastal_district(student_profile.district.name)
            
        return {
            "by_country": by_country,
            "by_career": by_career,
            "top_opportunities": top_opps,
            "is_coastal_student": is_coastal,
            "total_count": len(all_opps),
        }

    def get_ayurveda_pathways(self) -> dict:
        courses = Course.objects.filter(
            Q(discipline__name__icontains='ayurveda') | 
            Q(name__in=['BAMS', 'BHMS', 'BSMS', 'BNYS'])
        ).select_related('discipline__field__stream').distinct()
        
        careers = Career.objects.filter(is_ayurveda_related=True).distinct()
        
        from core.models import College
        colleges = College.objects.filter(college_courses__course__in=courses).select_related('district').distinct()
        
        gulf_demand = any(c.gulf_opportunity for c in careers)
        
        return {
            "courses": list(courses),
            "careers": list(careers),
            "colleges": list(colleges),
            "kerala_context": f"Kerala is the global capital of Ayurveda. The state has {colleges.count()} Ayurveda colleges offering BAMS, BHMS, and related programs. The Kerala model of Ayurveda combines traditional therapies with modern diagnostic protocols.",
            "gulf_demand": gulf_demand,
            "exam_required": "NEET-UG is required for BAMS admission in Kerala out of the State/All India quota. KEAM registration is mandatory.",
        }

    def get_tourism_pathways(self) -> dict:
        courses = Course.objects.filter(
            Q(is_tourism_related=True) |
            Q(discipline__name__icontains='tourism') |
            Q(discipline__name__icontains='hospitality') |
            Q(discipline__name__icontains='hotel')
        ).distinct()
        
        careers = Career.objects.filter(is_tourism_related=True).distinct()
        
        districts = District.objects.filter(
            name__in=['Ernakulam', 'Thiruvananthapuram', 'Kozhikode', 'Alappuzha', 'Thrissur', 'Wayanad', 'Idukki']
        )
        
        return {
            "courses": list(courses),
            "careers": list(careers),
            "top_districts": list(districts),
            "kerala_context": "Kerala Tourism is a globally recognized brand and a massive pillar of the state's economy. From backwater houseboats to hill station resorts, the scope is immense.",
            "industry_size": "₹40,000 crore",
            "annual_tourists_millions": 20,
            "gulf_connection": "Hospitality professionals from Kerala are in extremely high demand in Gulf hotels and luxury resorts, often progressing to management roles rapidly due to bilingual capabilities and service standards.",
        }

    def is_coastal_district(self, district_name: str) -> bool:
        return district_name in COASTAL_DISTRICTS
