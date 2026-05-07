from django.views.generic import View, DetailView, ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count
from core.models import College, CollegeCourse
from core.models import Stream, Field, Discipline, Course
from core.models import Career, EntranceExam
from core.models import StudentRecommendation
from core.services.search_service import SearchService
from core.services.comparison_service import ComparisonService
from core.services.career_service import CareerService

class CollegeListView(View):
    def get(self, request, *args, **kwargs):
        filters = {k: v for k, v in request.GET.items() if v}
        
        # handle multi-value naac_grade
        naac = request.GET.getlist('naac_grade')
        if naac:
            filters['naac_grade'] = naac
            
        page = int(request.GET.get('page', 1))
        
        search_svc = SearchService()
        result = search_svc.search_colleges(filters, page=page)
        filter_options = search_svc.get_filter_options()
        
        active_filters = {k: v for k, v in filters.items() if k not in ['page', 'sort']}
        
        context = {
            'result': result,
            'filter_options': filter_options,
            'active_filters': active_filters,
            'active_filter_count': len(active_filters),
        }
        return render(request, 'core/discovery/college_list.html', context)

class CollegeDetailView(DetailView):
    model = College
    template_name = 'core/discovery/college_detail.html'
    context_object_name = 'college'
    
    def get_queryset(self):
        return College.objects.select_related('district', 'university').prefetch_related(
            'college_courses__course__discipline__field__stream',
            'college_courses__specialization',
            'college_courses__yearly_cutoffs'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        college = self.object
        
        courses_by_stream = {}
        ccs = college.college_courses.all()
        for cc in ccs:
            if cc.course and cc.course.discipline and cc.course.discipline.field and cc.course.discipline.field.stream:
                stream_name = cc.course.discipline.field.stream.name
                if stream_name not in courses_by_stream:
                    courses_by_stream[stream_name] = []
                courses_by_stream[stream_name].append(cc)
                
        context['courses_by_stream'] = courses_by_stream
        context['total_courses'] = ccs.count()
        
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student_profile'):
            profile = self.request.user.student_profile
            context['student_recommendations'] = StudentRecommendation.objects.filter(
                student=profile,
                college_course__college=college
            )
            career_svc = CareerService()
            context['eligible_scholarships'] = career_svc.get_eligible_scholarships(profile)[:3]
            
        return context

class CourseListView(View):
    def get(self, request, *args, **kwargs):
        filters = {k: v for k, v in request.GET.items() if v}
        page = int(request.GET.get('page', 1))
        
        search_svc = SearchService()
        result = search_svc.search_courses(filters, page=page)
        filter_options = search_svc.get_filter_options()
        
        active_filters = {k: v for k, v in filters.items() if k not in ['page', 'sort']}
        
        if request.user.is_authenticated and hasattr(request.user, 'student_profile'):
            profile = request.user.student_profile
            recommended_cc_ids = set(StudentRecommendation.objects.filter(student=profile).values_list('college_course_id', flat=True))
            for cc in result['college_courses']:
                cc.is_recommended = cc.id in recommended_cc_ids
                
        context = {
            'result': result,
            'filter_options': filter_options,
            'active_filters': active_filters,
            'active_filter_count': len(active_filters),
        }
        return render(request, 'core/discovery/course_list.html', context)

class CourseDetailView(DetailView):
    model = Course
    template_name = 'core/discovery/course_detail.html'
    context_object_name = 'course'
    
    def get_queryset(self):
        return Course.objects.select_related('discipline__field__stream')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        
        ccs = CollegeCourse.objects.filter(course=course).select_related(
            'college__district', 'college__university'
        ).order_by('cutoff_general')
        
        # Paginate 10 per page
        page = self.request.GET.get('page', 1)
        from django.core.paginator import Paginator
        paginator = Paginator(ccs, 10)
        context['college_courses'] = paginator.get_page(page)
        
        career_svc = CareerService()
        context['entrance_exams'] = career_svc.get_exams_for_course(course)
        context['career_outcomes'] = course.career_outcomes.all()[:6]
        
        context['stream_path'] = {
            "stream": course.discipline.field.stream.name if course.discipline and course.discipline.field else "",
            "field": course.discipline.field.name if course.discipline else "",
            "discipline": course.discipline.name if course.discipline else "",
            "course": course.name,
        }
        
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student_profile'):
            profile = self.request.user.student_profile
            if profile.plus_two_percentage is not None and course.min_percentage_required is not None:
                context['student_eligible'] = profile.plus_two_percentage >= (course.min_percentage_required - 5)
            else:
                context['student_eligible'] = False
            
            context['eligible_scholarships'] = career_svc.get_eligible_scholarships(profile)[:3]
            
        return context

class StreamListView(View):
    def get(self, request, *args, **kwargs):
        streams = Stream.objects.filter(is_active=True).annotate(
            field_count=Count('fields', distinct=True),
            discipline_count=Count('fields__disciplines', distinct=True),
            total_course_count=Count('fields__disciplines__courses__college_courses', distinct=True)
        )
        context = {'streams': streams}
        return render(request, 'core/discovery/stream_list.html', context)

class StreamDetailView(DetailView):
    model = Stream
    template_name = 'core/discovery/stream_detail.html'
    context_object_name = 'stream'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stream = self.object
        
        fields = stream.fields.filter(is_active=True).prefetch_related('disciplines')
        fields_with_disciplines = {}
        total_disciplines = 0
        total_courses = 0
        
        for field in fields:
            fields_with_disciplines[field] = []
            disciplines = field.disciplines.filter(is_active=True).annotate(
                course_count=Count('courses')
            )
            total_disciplines += disciplines.count()
            for disc in disciplines:
                top_courses = disc.courses.all()[:3]
                fields_with_disciplines[field].append({
                    'discipline': disc,
                    'top_courses': top_courses
                })
                total_courses += disc.course_count
                
        context['fields_with_disciplines'] = fields_with_disciplines
        context['total_disciplines'] = total_disciplines
        context['total_courses'] = total_courses
        
        context['related_careers'] = Career.objects.filter(
            qualifying_courses__discipline__field__stream=stream
        ).distinct()[:6]
        
        # Exams for courses in this stream
        context['entrance_exams'] = EntranceExam.objects.filter(
            courses_unlocked__discipline__field__stream=stream
        ).distinct()[:5]
        
        return context

class CompareCollegesView(View):
    def get(self, request, *args, **kwargs):
        ids_param = request.GET.get('ids', '')
        course_id = request.GET.get('course')
        
        if not ids_param or not course_id:
            return redirect('discovery:college_list')
            
        try:
            college_ids = [int(i) for i in ids_param.split(',')]
            course_id = int(course_id)
        except ValueError:
            return redirect('discovery:college_list')
            
        comp_svc = ComparisonService()
        try:
            comparison = comp_svc.compare_colleges(college_ids, course_id)
        except ValueError as e:
            # e.g., bad id count
            from django.contrib import messages
            messages.error(request, str(e))
            return redirect('discovery:college_list')
            
        context = {
            'comparison': comparison,
            'share_url': request.build_absolute_uri(),
        }
        return render(request, 'core/discovery/compare_colleges.html', context)

class CompareCoursesView(View):
    def get(self, request, *args, **kwargs):
        ids_param = request.GET.get('ids', '')
        
        if not ids_param:
            return redirect('discovery:course_list')
            
        try:
            cc_ids = [int(i) for i in ids_param.split(',')]
        except ValueError:
            return redirect('discovery:course_list')
            
        comp_svc = ComparisonService()
        try:
            comparison = comp_svc.compare_courses(cc_ids)
        except ValueError as e:
            from django.contrib import messages
            messages.error(request, str(e))
            return redirect('discovery:course_list')
            
        context = {
            'comparison': comparison,
            'share_url': request.build_absolute_uri(),
        }
        return render(request, 'core/discovery/compare_courses.html', context)

class QuickSearchView(View):
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '').strip()
        search_svc = SearchService()
        results = search_svc.quick_search(q)
        
        # Check if requested by AJAX (Django 4+ standard way)
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        if is_ajax:
            return JsonResponse(results)
            
        # Non-AJAX renders a full page
        context = {'search_dict': results}
        return render(request, 'core/discovery/search_results.html', context)
