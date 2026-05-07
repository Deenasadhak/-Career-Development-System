from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

from core.models import Career, CareerCategory, EntranceExam, Scholarship
from core.models import StudentProfile
from core.services.career_service import CareerService

class CareerListView(ListView):
    template_name = 'core/careers/list.html'
    context_object_name = 'careers'
    paginate_by = 12

    def get_queryset(self):
        qs = Career.objects.filter(is_active=True).select_related('category')
        
        category_slug = self.request.GET.get('category')
        if category_slug:
            qs = qs.filter(Q(category__slug=category_slug) | Q(category__parent__slug=category_slug))
            
        demand = self.request.GET.get('demand')
        if demand in ['HIGH', 'MEDIUM', 'LOW']:
            qs = qs.filter(job_demand=demand)
            
        gulf = self.request.GET.get('gulf')
        if gulf == 'true':
            qs = qs.filter(gulf_opportunity=True)
            
        search_kw = self.request.GET.get('search')
        if search_kw:
            qs = qs.filter(Q(title__icontains=search_kw) | Q(description__icontains=search_kw))
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CareerCategory.objects.filter(parent__isnull=True).prefetch_related('subcategories')
        context['selected_category'] = self.request.GET.get('category', '')
        context['demand_filter'] = self.request.GET.get('demand', '')
        context['gulf_filter'] = self.request.GET.get('gulf', '')
        
        if self.request.user.is_authenticated:
            try:
                student = StudentProfile.objects.get(user=self.request.user)
                svc = CareerService()
                context['recommended_careers'] = svc.get_careers_for_student(student, limit=4)
            except StudentProfile.DoesNotExist:
                pass
                
        return context

class CareerDetailView(DetailView):
    model = Career
    template_name = 'core/careers/detail.html'
    context_object_name = 'career'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        career = self.object
        svc = CareerService()
        
        context['career_path'] = svc.get_career_path(career)
        qc = career.qualifying_courses.select_related('discipline__field__stream')[:6]
        context['qualifying_courses'] = qc
        
        exams = []
        for course in qc:
            exams.extend(svc.get_exams_for_course(course))
        
        # Deduplicate
        seen = set()
        unique_exams = []
        for e in exams:
            if e.id not in seen:
                seen.add(e.id)
                unique_exams.append(e)
                
        context['entrance_exams'] = unique_exams
        context['related_careers'] = career.related_careers.all()[:4]
        
        context['is_eligible_for_any_course'] = False
        if self.request.user.is_authenticated:
            try:
                sp = StudentProfile.objects.get(user=self.request.user)
                if sp.plus_two_percentage:
                    # simplistic check: is there any CollegeCourse for these qualifying courses with cutoff <= student %
                    from core.models import CollegeCourse
                    c_ids = [c.id for c in qc]
                    has_course = CollegeCourse.objects.filter(
                        course_id__in=c_ids, 
                        cutoff_general__lte=sp.plus_two_percentage
                    ).exists()
                    context['is_eligible_for_any_course'] = has_course
            except StudentProfile.DoesNotExist:
                pass
                
        return context

class CareerCategoryView(ListView):
    template_name = 'core/careers/category.html'
    context_object_name = 'careers'
    paginate_by = 12

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return Career.objects.filter(
            Q(category__slug=slug) | Q(category__parent__slug=slug),
            is_active=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(CareerCategory, slug=self.kwargs.get('slug'))
        context['category'] = category
        context['subcategories'] = category.subcategories.all()
        return context

class EntranceExamListView(ListView):
    template_name = 'core/exams/list.html'
    context_object_name = 'exams'
    
    def get_queryset(self):
        return [] # We use context instead

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        svc = CareerService()
        calendar = svc.get_exam_calendar()
        
        state = [item for item in calendar if item['exam'].level == 'STATE']
        national = [item for item in calendar if item['exam'].level == 'NATIONAL']
        university = [item for item in calendar if item['exam'].level == 'UNIVERSITY']
        
        context['grouped_exams'] = {
            'STATE': state,
            'NATIONAL': national,
            'UNIVERSITY': university
        }
        context['exam_calendar'] = calendar
        return context

class EntranceExamDetailView(DetailView):
    model = EntranceExam
    template_name = 'core/exams/detail.html'
    context_object_name = 'exam'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group courses_unlocked by stream
        courses = self.object.courses_unlocked.select_related('discipline__field__stream')
        grouped = {}
        for c in courses:
            stream_name = c.discipline.field.stream.name if (c.discipline and c.discipline.field and c.discipline.field.stream) else 'Other'
            if stream_name not in grouped:
                grouped[stream_name] = []
            grouped[stream_name].append(c)
        context['courses_by_stream'] = grouped
        return context

class ScholarshipListView(ListView):
    template_name = 'core/scholarships/list.html'
    context_object_name = 'scholarships'
    paginate_by = 15

    def get_queryset(self):
        qs = Scholarship.objects.filter(is_active=True)
        type_filter = self.request.GET.get('type')
        if type_filter:
            qs = qs.filter(scholarship_type=type_filter)
        if self.request.GET.get('kerala') == 'true':
            qs = qs.filter(is_kerala_specific=True)
        return qs

class EligibleScholarshipsView(LoginRequiredMixin, ListView):
    template_name = 'core/scholarships/eligible.html'
    context_object_name = 'scholarships'

    def get_queryset(self):
        try:
            student = StudentProfile.objects.get(user=self.request.user)
            svc = CareerService()
            return svc.get_eligible_scholarships(student)
        except StudentProfile.DoesNotExist:
            return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.get_queryset()
        
        grouped = {}
        total_val = 0
        for s in items:
            t = s.get_scholarship_type_display()
            if t not in grouped:
                grouped[t] = []
            grouped[t].append(s)
            total_val += s.amount_per_year
            
        context['grouped_scholarships'] = grouped
        context['total_value'] = total_val
        
        if not items:
            context['help_message'] = "We couldn't find any scholarships matching your profile. Make sure your community, annual income, Plus Two marks, and category details are thoroughly filled out in your profile."
            
        return context

class GulfCareersView(ListView):
    template_name = 'core/careers/gulf.html'
    context_object_name = 'careers'

    def get_queryset(self):
        return Career.objects.filter(is_active=True, gulf_opportunity=True).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.get_queryset()
        
        grouped = {}
        for c in items:
            cat = c.category.name if c.category else 'Other'
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(c)
            
        context['grouped_careers'] = grouped
        context['coastal_districts'] = ['Thiruvananthapuram', 'Kollam', 'Alappuzha', 'Ernakulam', 'Thrissur', 'Malappuram', 'Kozhikode', 'Kannur', 'Kasaragod']
        context['career_count'] = items.count()
        return context
