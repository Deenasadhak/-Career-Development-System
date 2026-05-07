from django.db.models import Count, Avg, Sum, Q, F, FloatField, ExpressionWrapper, Case, When
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from django.contrib.auth import get_user_model

from core.models import College, CollegeCourse
from core.models import Course
from core.models import Career, Scholarship
from core.models import StudentProfile
from core.models import TestSession, AptitudeQuestion
from core.models import StudentRecommendation
from core.models import District

User = get_user_model()

class AnalyticsService:

    def get_super_admin_overview(self) -> dict:
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        if month_start.month == 1:
            last_month_start = month_start.replace(year=month_start.year - 1, month=12)
        else:
            last_month_start = month_start.replace(month=month_start.month - 1)
            
        week_ago = timezone.now() - timedelta(days=7)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        students_qs = User.objects.filter(role='STUDENT')
        
        total_students = students_qs.count()
        total_colleges = College.objects.count()
        total_courses = CollegeCourse.objects.count()
        total_careers = Career.objects.count()
        total_questions = AptitudeQuestion.objects.count()
        total_scholarships = Scholarship.objects.count()

        students_this_month = students_qs.filter(date_joined__date__gte=month_start).count()
        students_last_month = students_qs.filter(date_joined__date__gte=last_month_start, date_joined__date__lt=month_start).count()
        students_this_week = students_qs.filter(date_joined__gte=week_ago).count()
        
        growth_pct = 0.0
        if students_last_month > 0:
            growth_pct = ((students_this_month - students_last_month) / students_last_month) * 100.0

        tests_taken_today = TestSession.objects.filter(started_at__date=today).count()
        tests_taken_this_week = TestSession.objects.filter(started_at__gte=week_ago).count()
        recommendations_generated_today = StudentRecommendation.objects.filter(generated_at__date=today).count()
        profiles_completed_today = StudentProfile.objects.filter(is_profile_complete=True, updated_at__date=today).count()

        top_colleges_qs = College.objects.annotate(
            recommendation_count=Count('college_courses__studentrecommendation'),
            shortlist_count=Count('college_courses__shortlistnote')
        ).order_by('-recommendation_count')[:10]
        
        top_colleges = [
            {
                "college_name": c.name,
                "district": c.district.name if c.district else "",
                "recommendation_count": c.recommendation_count,
                "shortlist_count": c.shortlist_count,
            }
            for c in top_colleges_qs
        ]

        top_courses_qs = CollegeCourse.objects.annotate(
            recommendation_count=Count('studentrecommendation')
        ).select_related('course__discipline__field__stream').order_by('-recommendation_count')[:10]
        
        top_courses = [
            {
                "course_name": cc.course.name,
                "stream": cc.course.discipline.field.stream.name if cc.course.discipline and cc.course.discipline.field else "",
                "recommendation_count": cc.recommendation_count,
            }
            for cc in top_courses_qs
        ]

        district_registrations = {d.name: 0 for d in District.objects.all()}
        dist_counts = StudentProfile.objects.exclude(district__isnull=True).values('district__name').annotate(count=Count('id'))
        for dc in dist_counts:
            district_registrations[dc['district__name']] = dc['count']

        stream_interest = {}
        stream_counts = StudentProfile.interest_streams.through.objects.values('stream__name').annotate(count=Count('studentprofile'))
        for sc in stream_counts:
            stream_interest[sc['stream__name']] = sc['count']

        test_sessions = TestSession.objects.all()
        total_sessions = test_sessions.count()
        completed_sessions = test_sessions.filter(status='COMPLETED').count()
        
        avg_scores = test_sessions.filter(status='COMPLETED').aggregate(
            Avg('logical_score'),
            Avg('quantitative_score'),
            Avg('verbal_score'),
            Avg('technical_score'),
            Avg('arts_score')
        )
        
        most_recommended_stream = None
        mrs_data = test_sessions.exclude(recommended_stream__isnull=True).values('recommended_stream__name').annotate(c=Count('id')).order_by('-c').first()
        if mrs_data:
            most_recommended_stream = mrs_data['recommended_stream__name']

        assessment_stats = {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "avg_logical_score": avg_scores['logical_score__avg'] or 0.0,
            "avg_quantitative_score": avg_scores['quantitative_score__avg'] or 0.0,
            "avg_verbal_score": avg_scores['verbal_score__avg'] or 0.0,
            "avg_technical_score": avg_scores['technical_score__avg'] or 0.0,
            "avg_arts_score": avg_scores['arts_score__avg'] or 0.0,
            "most_recommended_stream": most_recommended_stream,
        }

        registration_chart_data = []
        reg_counts = User.objects.filter(role='STUDENT', date_joined__gte=thirty_days_ago).extra({'date':"date(date_joined)"}).values('date').annotate(count=Count('id')).order_by('date')
        
        reg_dict = {str(item['date']): item['count'] for item in reg_counts}
        for i in range(30):
            d = (today - timedelta(days=29-i)).strftime('%Y-%m-%d')
            registration_chart_data.append({
                "date": d,
                "count": reg_dict.get(d, 0)
            })

        return {
            "totals": {
                "students": total_students,
                "colleges": total_colleges,
                "courses": total_courses,
                "careers": total_careers,
                "questions": total_questions,
                "scholarships": total_scholarships,
            },
            "growth": {
                "students_this_month": students_this_month,
                "students_last_month": students_last_month,
                "students_this_week": students_this_week,
                "growth_pct": round(growth_pct, 1),
            },
            "engagement": {
                "tests_taken_today": tests_taken_today,
                "tests_taken_this_week": tests_taken_this_week,
                "recommendations_generated_today": recommendations_generated_today,
                "profiles_completed_today": profiles_completed_today,
            },
            "top_colleges": top_colleges,
            "top_courses": top_courses,
            "district_registrations": district_registrations,
            "stream_interest": stream_interest,
            "assessment_stats": assessment_stats,
            "registration_chart_data": registration_chart_data,
        }

    def get_college_admin_stats(self, college) -> dict:
        fields_to_check = [
            college.name, college.district, college.university,
            college.phone, college.email, college.website
        ]
        filled_fields = sum(1 for f in fields_to_check if f)
        if college.naac_grade and college.naac_grade != 'NA':
            filled_fields += 1
            
        course_count = CollegeCourse.objects.filter(college=college, is_active=True).count()
        if course_count > 0:
            filled_fields += 1
            
        total_fields = len(fields_to_check) + 2
        pct = (filled_fields / total_fields) * 100.0

        total_seats = CollegeCourse.objects.filter(college=college, is_active=True).aggregate(s=Sum('total_intake'))['s'] or 0
        
        week_ago = timezone.now() - timedelta(days=7)
        recs = StudentRecommendation.objects.filter(college_course__college=college)
        total_recommended = recs.count()
        shortlisted = recs.filter(shortlistnote__isnull=False).distinct().count()
        eligible_count = recs.filter(eligibility_status='ELIGIBLE').count()
        this_week = recs.filter(generated_at__gte=week_ago).count()

        course_breakdown = []
        ccs = CollegeCourse.objects.filter(college=college).select_related('course', 'specialization').annotate(
            rec_count=Count('studentrecommendation', distinct=True),
            short_count=Count('shortlistnote', distinct=True)
        )
        for cc in ccs:
            course_breakdown.append({
                "course_name": cc.course.name,
                "specialization": cc.specialization.name if cc.specialization else None,
                "intake": cc.total_intake or 0,
                "cutoff_general": cc.cutoff_general,
                "tuition_fee": cc.tuition_fee or 0.0,
                "recommendation_count": cc.rec_count,
                "shortlist_count": cc.short_count,
            })

        dist_counts = recs.exclude(student__district__isnull=True).values('student__district__name').annotate(c=Count('id', distinct=True)).order_by('-c')[:5]
        top_districts = [{"district": d['student__district__name'], "count": d['c']} for d in dist_counts]

        return {
            "college_name": college.name,
            "profile_complete": filled_fields >= 8,
            "profile_completion_pct": round(pct, 1),
            "courses_offered": course_count,
            "total_seats": total_seats,
            "recommendation_stats": {
                "total_recommended": total_recommended,
                "shortlisted": shortlisted,
                "eligible_count": eligible_count,
                "this_week": this_week,
            },
            "course_breakdown": course_breakdown,
            "top_student_districts": top_districts,
            "profile_views_placeholder": None,  # TODO: Implement CollegeProfileView model
        }

    def get_monthly_chart_data(self, months: int = 6) -> dict:
        labels = []
        students_registered = []
        tests_taken = []
        recommendations_generated = []
        
        today = timezone.now().date()
        for i in range(months-1, -1, -1):
            target_month = today.replace(day=1)
            for _ in range(i):
                if target_month.month == 1:
                    target_month = target_month.replace(year=target_month.year - 1, month=12)
                else:
                    target_month = target_month.replace(month=target_month.month - 1)
                    
            next_month = target_month.replace(month=target_month.month+1) if target_month.month < 12 else target_month.replace(year=target_month.year+1, month=1)
            
            labels.append(target_month.strftime('%b %Y'))
            
            sc = User.objects.filter(role='STUDENT', date_joined__date__gte=target_month, date_joined__date__lt=next_month).count()
            students_registered.append(sc)
            
            tc = TestSession.objects.filter(started_at__date__gte=target_month, started_at__date__lt=next_month).count()
            tests_taken.append(tc)
            
            rc = StudentRecommendation.objects.filter(generated_at__date__gte=target_month, generated_at__date__lt=next_month).count()
            recommendations_generated.append(rc)

        return {
            "labels": labels,
            "students_registered": students_registered,
            "tests_taken": tests_taken,
            "recommendations_generated": recommendations_generated,
        }

    def get_question_analytics(self) -> dict:
        qs = AptitudeQuestion.objects.annotate(
            success_rate=Case(
                When(times_used=0, then=None),
                default=ExpressionWrapper(F('correct_count') * 100.0 / F('times_used'), output_field=FloatField()),
                output_field=FloatField()
            )
        )
        
        total_questions = qs.count()
        active_questions = qs.filter(is_active=True).count()
        never_used_count = qs.filter(times_used=0).count()
        
        categories = qs.values('category__name').annotate(
            total=Count('id'),
            easy=Count('id', filter=Q(difficulty='E')),
            medium=Count('id', filter=Q(difficulty='M')),
            hard=Count('id', filter=Q(difficulty='H')),
            avg_sr=Avg('success_rate')
        )
        
        by_category = []
        low_cats = []
        for c in categories:
            by_category.append({
                "category": c['category__name'] or "Uncategorized",
                "total": c['total'],
                "easy": c['easy'],
                "medium": c['medium'],
                "hard": c['hard'],
                "avg_success_rate": c['avg_sr'] or 0.0,
            })
            if c['total'] < 10:
                low_cats.append(c['category__name'] or "Uncategorized")
                
        low_success_rate_questions = list(qs.filter(times_used__gt=5, success_rate__lt=30.0).order_by('success_rate')[:10])
        lsr_out = []
        for q in low_success_rate_questions:
            lsr_out.append({
                "id": q.id,
                "text": (q.question_text[:77] + "...") if len(q.question_text) > 80 else q.question_text,
                "category": q.category.name if q.category else "None",
                "success_rate": q.success_rate,
                "times_used": q.times_used,
            })
            
        return {
            "total_questions": total_questions,
            "active_questions": active_questions,
            "by_category": by_category,
            "low_question_categories": low_cats,
            "never_used_count": never_used_count,
            "low_success_rate_questions": lsr_out,
        }
