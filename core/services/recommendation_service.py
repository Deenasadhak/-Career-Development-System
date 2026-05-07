# core/services/recommendation_service.py

from core.models import College, Course, CollegeCourse, CareerPath

# From Ranking_Legend sheet
NAAC_BONUS = {
    'A++': 20, 'A+': 15, 'A': 10, 'B+': 5, 'B': 0, 'C': -5
}

STREAM_ELIGIBILITY = {
    'Science': ['Science'],
    'Commerce': ['Commerce', 'Science', 'Any', 
                 'Commerce / Science', 'Commerce / Science / Arts',
                 'Commerce / Arts'],
    'Arts': ['Arts', 'Any', 'Commerce / Arts', 
             'Commerce / Science / Arts', 'Arts / Commerce',
             'Arts / Science', 'Arts / Commerce / Science'],
}

def get_cutoff_info(cutoff):
    if cutoff >= 550:
        return {'label': 'Elite', 'badge': 'bg-danger', 'strategy': 'Need top percentile + coaching'}
    elif cutoff >= 480:
        return {'label': 'High', 'badge': 'bg-warning text-dark', 'strategy': 'Strong academics required'}
    elif cutoff >= 400:
        return {'label': 'Medium', 'badge': 'bg-info text-dark', 'strategy': 'Merit + entrance focus'}
    elif cutoff >= 350:
        return {'label': 'Low', 'badge': 'bg-primary', 'strategy': 'Available across streams'}
    else:
        return {'label': 'Open', 'badge': 'bg-secondary', 'strategy': 'Management quota available'}

def get_recommendations(student_stream, student_percentage, 
                        aptitude_score, student_district=None,
                        max_cutoff=600):
    """
    Returns top 10 CollegeCourse objects ranked by fit score.
    
    Scoring (total 100 points):
    - Aptitude (40pts): aptitude_score normalized to 600
    - Academic (20pts): 12th percentage
    - Demand (20pts): course kerala_demand_score from dataset
    - NAAC bonus (10pts): from Ranking_Legend sheet
    - Stream match (10pts): exact stream eligibility
    """
    
    results = []
    
    # Get all active college-course combinations
    qs = CollegeCourse.objects.filter(
        is_active=True,
        cutoff_general__lte=max_cutoff
    ).select_related('college', 'course')
    
    for cc in qs:
        course = cc.course
        college = cc.college
        
        # Check stream eligibility using eligible_streams field from dataset
        eligible = False
        student_eligible_streams = STREAM_ELIGIBILITY.get(student_stream, [])
        for eligible_stream in student_eligible_streams:
            if (eligible_stream.lower() in course.eligible_streams.lower() or
                course.stream == student_stream or
                'any' in course.eligible_streams.lower()):
                eligible = True
                break
        
        if not eligible:
            continue
        
        # Check minimum percentage eligibility
        if student_percentage < course.min_percentage:
            continue
        
        # ── SCORING ──────────────────────────────────────────────
        
        # 1. Aptitude component (40 pts)
        # Assuming aptitude_score passed is out of 150 (raw)
        # We scale it to 600 for comparison and normalization
        aptitude_scaled = (aptitude_score / 150) * 600
        aptitude_normalized = min(aptitude_scaled / 600, 1.0)
        aptitude_pts = aptitude_normalized * 40
        
        # 2. Academic component (20 pts)
        academic_pts = (student_percentage / 100) * 20
        
        # 3. Demand component (20 pts) — from dataset
        demand_pts = (course.kerala_demand_score / 100) * 20
        
        # 4. NAAC bonus (10 pts) — from Ranking_Legend
        naac_pts = (NAAC_BONUS.get(college.naac_grade, -10) / 20) * 10
        naac_pts = max(0, naac_pts)  # floor at 0
        
        # 5. Stream match (10 pts)
        stream_pts = 10 if course.stream == student_stream else 5
        
        total_score = (aptitude_pts + academic_pts + 
                       demand_pts + naac_pts + stream_pts)
        fit_score = round(min(total_score, 100), 1)
        
        # Eligibility flag
        is_eligible = aptitude_scaled >= cc.cutoff_general
        
        # Get career path from dataset
        career = None
        try:
            career = course.career_paths.first()
        except:
            pass
        
        results.append({
            'college_course': cc,
            'college': college,
            'course': course,
            'fit_score': fit_score,
            'is_eligible': is_eligible,
            'cutoff_mark': cc.cutoff_general,
            'cutoff_info': get_cutoff_info(cc.cutoff_general),
            'min_percentage': course.min_percentage,
            'cap_applicable': course.cap_applicable,
            'duration': course.duration_years,
            'competitiveness': 'N/A',
            'naac_grade': college.naac_grade,
            'naac_bonus': NAAC_BONUS.get(college.naac_grade, -10),
            'demand_score': course.kerala_demand_score,
            'fee_per_year': cc.fee_per_year,
            'gulf_opportunity': career.gulf_opportunity if career else 'Unknown',
            'avg_salary': career.avg_salary_kerala if career else course.avg_salary_kerala,
            'job_roles': career.top_job_roles if career else course.top_job_roles,
            'top_employers': career.top_employers if career else '',
            'further_studies': career.further_studies if career else '',
            'psc_relevant': course.psc_relevant,
            'hostel': college.hostel_available,
            'district': college.district,
            'university': college.university,
            'nirf_state': college.nirf_state_rank,
            'reason': build_reason(course, college, fit_score, 
                                   is_eligible, career),
        })
    
    # Sort by fit_score descending, eligible colleges first
    results.sort(key=lambda x: (x['is_eligible'], x['fit_score']), 
                 reverse=True)
    
    return results[:10]


def build_reason(course, college, fit_score, is_eligible, career):
    reasons = []
    if college.naac_grade in ['A++', 'A+']:
        reasons.append(f"Top-rated {college.naac_grade} institution")
    if course.kerala_demand_score >= 85:
        reasons.append("Very high job demand in Kerala")
    elif course.kerala_demand_score >= 70:
        reasons.append("Good job demand in Kerala")
    if career and career.gulf_opportunity in ['Very High', 'High']:
        reasons.append(f"{career.gulf_opportunity} Gulf opportunity")
    if course.psc_relevant:
        reasons.append("PSC exam eligible")
    if college.nirf_state_rank and college.nirf_state_rank <= 5:
        reasons.append(f"Ranked #{college.nirf_state_rank} in Kerala")
    if not is_eligible:
        reasons.append("⚠️ Score below cutoff — management quota possible")
    return " • ".join(reasons) if reasons else "Good overall fit for your profile"
