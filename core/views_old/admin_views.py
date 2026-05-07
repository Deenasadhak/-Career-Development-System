import json
import csv
from datetime import datetime
from django.utils import timezone
from django.views.generic import View, ListView, UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count, F, FloatField, ExpressionWrapper, Case, When
from django.contrib.auth import get_user_model

from core.models import College, CollegeCourse
from core.models import District
from core.models import Stream
from core.models import AptitudeQuestion
from core.services.analytics_service import AnalyticsService

User = get_user_model()

class SuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and getattr(self.request.user, 'role', '') == 'SUPER_ADMIN'

    def handle_no_permission(self):
        from django.contrib import messages
        messages.error(self.request, "Super Admin access required.")
        return redirect('/')

class CollegeAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        role = getattr(self.request.user, 'role', '')
        return role in ['COLLEGE_ADMIN', 'SUPER_ADMIN']

    def handle_no_permission(self):
        from django.contrib import messages
        messages.error(self.request, "College Admin access required.")
        return redirect('/')

# --- SUPER ADMIN VIEWS ---

class SuperAdminDashboardView(SuperAdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        analytics = AnalyticsService()
        overview = analytics.get_super_admin_overview()
        monthly_data = analytics.get_monthly_chart_data(6)
        question_analytics = analytics.get_question_analytics()
        
        chart_data = {
            "registration_labels": [item['date'] for item in overview['registration_chart_data']],
            "registration_data": [item['count'] for item in overview['registration_chart_data']],
            "monthly_labels": monthly_data["labels"],
            "students_data": monthly_data["students_registered"],
            "tests_data": monthly_data["tests_taken"],
            "district_labels": list(overview['district_registrations'].keys()),
            "district_data": list(overview['district_registrations'].values()),
            "stream_labels": list(overview['stream_interest'].keys()),
            "stream_data": list(overview['stream_interest'].values()),
        }
        
        context = {
            'overview': overview,
            'monthly_data': monthly_data,
            'question_analytics': question_analytics,
            'json_data': json.dumps(chart_data, default=str),
        }
        return render(request, 'core/admin_dashboard/super_admin.html', context)

class StudentManagementView(SuperAdminRequiredMixin, ListView):
    model = User
    template_name = 'core/admin_dashboard/students.html'
    context_object_name = 'students'
    paginate_by = 25

    def get_queryset(self):
        qs = User.objects.filter(role='STUDENT').select_related('student_profile__district').prefetch_related(
            'student_profile__interest_streams', 'student_profile__test_sessions'
        )
        
        district_id = self.request.GET.get('district')
        stream_id = self.request.GET.get('stream')
        community = self.request.GET.get('community')
        profile_complete = self.request.GET.get('profile_complete')
        has_test = self.request.GET.get('has_test')
        search = self.request.GET.get('search')
        sort = self.request.GET.get('sort', 'date_joined')
        
        if district_id:
            qs = qs.filter(student_profile__district_id=district_id)
        if stream_id:
            qs = qs.filter(student_profile__interest_streams__id=stream_id)
        if community:
            qs = qs.filter(student_profile__community=community)
        if profile_complete == 'true':
            qs = qs.filter(student_profile__is_profile_complete=True)
        elif profile_complete == 'false':
            qs = qs.filter(student_profile__is_profile_complete=False)
        if has_test == 'true':
            qs = qs.filter(student_profile__test_sessions__isnull=False).distinct()
        elif has_test == 'false':
            qs = qs.filter(student_profile__test_sessions__isnull=True)
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(email__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search))
            
        if sort == 'percentage':
            qs = qs.order_by('-student_profile__plus_two_percentage')
        elif sort == 'district':
            qs = qs.order_by('student_profile__district__name')
        else:
            qs = qs.order_by('-date_joined')
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_options'] = {
            'districts': District.objects.all(),
            'streams': Stream.objects.filter(is_active=True),
        }
        context['active_filters'] = self.request.GET.dict()
        context['total_count'] = self.get_queryset().count()
        context['export_url'] = self.request.build_absolute_uri('/admin-dashboard/students/export/') + ('?' + self.request.GET.urlencode() if self.request.GET else '')
        return context

class Echo:
    def write(self, value):
        return value

class StudentExportView(SuperAdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        qs = User.objects.filter(role='STUDENT').select_related('student_profile__district').prefetch_related(
            'student_profile__interest_streams', 'student_profile__test_sessions'
        ).annotate(
            tests_taken=Count('student_profile__test_sessions', distinct=True),
            recs_count=Count('student_profile__recommendations', distinct=True)
        )
        
        # Apply filters equivalent to StudentManagementView here if needed, simplified for export speed
        
        def iter_items():
            yield [
                'email', 'full_name', 'date_joined', 'district', 'community', 
                'plus_two_percentage', 'plus_two_stream', 'keam_rank', 'neet_score', 
                'profile_complete', 'tests_taken', 'recommendations_count', 'interest_streams'
            ]
            for user in qs.iterator(chunk_size=1000):
                sp = getattr(user, 'student_profile', None)
                if not sp:
                    continue
                streams = "|".join([s.name for s in sp.interest_streams.all()])
                yield [
                    user.email, f"{user.first_name} {user.last_name}".strip(),
                    user.date_joined.strftime('%Y-%m-%d'),
                    sp.district.name if sp.district else '',
                    sp.community,
                    str(sp.plus_two_percentage) if sp.plus_two_percentage else '',
                    sp.plus_two_stream,
                    str(sp.keam_rank) if sp.keam_rank else '',
                    str(sp.neet_score) if sp.neet_score else '',
                    str(sp.is_profile_complete),
                    str(user.tests_taken),
                    str(user.recs_count),
                    streams
                ]

        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in iter_items()),
            content_type="text/csv"
        )
        today = timezone.now().date()
        response['Content-Disposition'] = f'attachment; filename="students_{today}.csv"'
        return response

class CollegeManagementView(SuperAdminRequiredMixin, ListView):
    model = College
    template_name = 'core/admin_dashboard/colleges.html'
    context_object_name = 'colleges'
    paginate_by = 25

    def get_queryset(self):
        qs = College.objects.select_related('district', 'university').annotate(
            course_count=Count('college_courses', distinct=True),
            recommendation_count=Count('college_courses__studentrecommendation', distinct=True)
        )
        
        district = self.request.GET.get('district')
        ctype = self.request.GET.get('type')
        verified = self.request.GET.get('verified')
        search = self.request.GET.get('search')
        sort = self.request.GET.get('sort', 'name')
        
        if district:
            qs = qs.filter(district_id=district)
        if ctype:
            qs = qs.filter(college_type=ctype)
        if verified == 'true':
            qs = qs.filter(is_verified=True)
        elif verified == 'false':
            qs = qs.filter(is_verified=False)
        if search:
            qs = qs.filter(name__icontains=search)
            
        if sort == 'courses':
            qs = qs.order_by('-course_count')
        elif sort == 'recommendations':
            qs = qs.order_by('-recommendation_count')
        else:
            qs = qs.order_by(sort)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_qs = College.objects.all()
        context['total_verified'] = base_qs.filter(is_verified=True).count()
        context['total_unverified'] = base_qs.filter(is_verified=False).count()
        
        types = base_qs.values('college_type').annotate(c=Count('id'))
        context['total_by_type'] = {t['college_type']: t['c'] for t in types}
        return context

class CollegeVerifyView(SuperAdminRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        college = get_object_or_404(College, pk=pk)
        college.is_verified = not college.is_verified
        college.save(update_fields=['is_verified'])
        return JsonResponse({"verified": college.is_verified, "college_id": college.pk})

class QuestionManagementView(SuperAdminRequiredMixin, ListView):
    model = AptitudeQuestion
    template_name = 'core/admin_dashboard/questions.html'
    context_object_name = 'questions'
    paginate_by = 30

    def get_queryset(self):
        qs = AptitudeQuestion.objects.annotate(
            success_rate=Case(
                When(times_used=0, then=None),
                default=ExpressionWrapper(F('correct_count') * 100.0 / F('times_used'), output_field=FloatField()),
                output_field=FloatField()
            )
        ).select_related('category')
        
        cat = self.request.GET.get('category')
        diff = self.request.GET.get('difficulty')
        active = self.request.GET.get('active')
        search = self.request.GET.get('search')
        
        if cat:
            qs = qs.filter(category_id=cat)
        if diff:
            qs = qs.filter(difficulty_level=diff)
        if active == 'true':
            qs = qs.filter(is_active=True)
        elif active == 'false':
            qs = qs.filter(is_active=False)
        if search:
            qs = qs.filter(text__icontains=search)
            
        qs = qs.order_by('-id')
        return qs

class QuestionBulkActivateView(SuperAdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            action = data.get('action')
            q_ids = data.get('question_ids', [])
            
            if action not in ['activate', 'deactivate']:
                return JsonResponse({"error": "Invalid action"}, status=400)
                
            is_active = (action == 'activate')
            updated = AptitudeQuestion.objects.filter(id__in=q_ids).update(is_active=is_active)
            return JsonResponse({"updated_count": updated, "action": action})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# --- COLLEGE ADMIN VIEWS ---

class CollegeAdminDashboardView(CollegeAdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            college = College.objects.get(admin_user=request.user)
        except College.DoesNotExist:
            return render(request, 'core/college_admin/not_assigned.html')
            
        analytics = AnalyticsService()
        stats = analytics.get_college_admin_stats(college)
        monthly_data = analytics.get_monthly_chart_data(3)
        
        c_names = [c['course_name'] for c in stats['course_breakdown']]
        c_recs = [c['recommendation_count'] for c in stats['course_breakdown']]
        
        chart_data = {
            "course_names": c_names,
            "course_recs": c_recs,
            "monthly_labels": monthly_data["labels"],
            "monthly_recs": monthly_data["recommendations_generated"],
        }
        
        recent = StudentRecommendation.objects.filter(college_course__college=college).select_related(
            'student__user', 'college_course__course'
        ).order_by('-generated_at')[:10]
        
        context = {
            'college': college,
            'stats': stats,
            'monthly_data': monthly_data,
            'chart_json': json.dumps(chart_data, default=str),
            'recent_recommendations': recent,
        }
        return render(request, 'core/college_admin/dashboard.html', context)

from django import forms
class CollegeProfileForm(forms.ModelForm):
    class Meta:
        model = College
        fields = [
            'phone', 'email', 'website', 'address',
            'nearest_railway_station', 'nearest_railway_km',
            'nearest_bus_stand', 'nearest_bus_km',
            'has_hostel_boys', 'has_hostel_girls',
            'has_transport', 'has_wifi', 'has_library',
            'has_sports', 'has_canteen', 'has_medical',
            'has_placement_cell', 'has_nss', 'has_ncc',
            'total_student_strength', 'campus_area_acres'
        ]

class CollegeProfileUpdateView(CollegeAdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            college = College.objects.get(admin_user=request.user)
        except College.DoesNotExist:
            return render(request, 'core/college_admin/not_assigned.html')
            
        form = CollegeProfileForm(instance=college)
        return render(request, 'core/college_admin/profile_update.html', {'form': form, 'college': college})

    def post(self, request, *args, **kwargs):
        try:
            college = College.objects.get(admin_user=request.user)
        except College.DoesNotExist:
            return render(request, 'core/college_admin/not_assigned.html')
            
        form = CollegeProfileForm(request.POST, instance=college)
        from django.contrib import messages
        if form.is_valid():
            form.save()
            messages.success(request, "College profile updated successfully.")
            return redirect('college_admin:dashboard')
        else:
            messages.error(request, "Error updating profile. Please correct the errors below.")
            return render(request, 'core/college_admin/profile_update.html', {'form': form, 'college': college})

class CollegeCourseManagementView(CollegeAdminRequiredMixin, ListView):
    template_name = 'core/college_admin/courses.html'
    context_object_name = 'courses'

    def get_queryset(self):
        try:
            college = College.objects.get(admin_user=self.request.user)
            return CollegeCourse.objects.filter(college=college).select_related('course').annotate(
                rec_count=Count('studentrecommendation', distinct=True),
                short_count=Count('shortlistnote', distinct=True)
            )
        except College.DoesNotExist:
            return CollegeCourse.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['college'] = College.objects.get(admin_user=self.request.user)
        except College.DoesNotExist:
            pass
        return context

class CollegeCourseUpdateView(CollegeAdminRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        cc = get_object_or_404(CollegeCourse, pk=pk)
        
        try:
            admin_college = College.objects.get(admin_user=request.user)
            if cc.college_id != admin_college.pk:
                return JsonResponse({"success": False, "error": "Forbidden"}, status=403)
        except College.DoesNotExist:
            return JsonResponse({"success": False, "error": "Forbidden"}, status=403)
            
        data = json.loads(request.body)
        allowed_fields = [
            'tuition_fee', 'hostel_fee', 'transport_fee',
            'cutoff_general', 'cutoff_sc', 'cutoff_st',
            'cutoff_obc', 'placement_percentage',
            'avg_package_lpa', 'highest_package_lpa',
            'top_recruiters', 'total_intake'
        ]
        
        for field in allowed_fields:
            if field in data:
                # Handle special case if total_intake mapped to total_seats in model
                # User request allowed total_intake as field alias probably, or maybe meant total_seats
                if field == 'total_intake' and hasattr(cc, 'total_seats'):
                    setattr(cc, 'total_seats', data[field])
                elif hasattr(cc, field):
                    setattr(cc, field, data[field])
                    
        cc.save()
        return JsonResponse({"success": True, "message": "Updated successfully"})
