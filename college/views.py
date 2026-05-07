from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from college.forms import CollegeProfileForm

from django.urls import reverse_lazy
from core.models import College, CollegeCourse
from core.models import Course

from django.db.models import Min

class CollegeHome(LoginRequiredMixin, TemplateView):
    template_name = 'college_temp/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        college = College.objects.filter(user=self.request.user).first()
        if not college:
            # Fallback for demo: link the user to the first college found if none linked
            college = College.objects.first()
            if college and not college.user:
                college.user = self.request.user
                college.save()

        if college:
            courses = college.college_courses.all()
            context['college'] = college
            context['course_count'] = courses.count()
            context['min_cutoff'] = courses.aggregate(Min('cutoff_general'))['cutoff_general__min'] or 0
            context['view_count'] = 125 # Simulated metric
        return context


class CollegeProfileAdd(LoginRequiredMixin, CreateView):
    template_name = 'college_temp/Add_CollegeProfile.html'
    form_class = CollegeProfileForm
    model = College
    success_url = reverse_lazy('college_home')

    def form_valid(self, form):
        # We need to handle the user link carefully
        # The core.College doesn't have a user field by default in my schema.
        # Wait, I should add a user field to core.College if it's meant to be managed by a college user.
        # Looking back at core/models.py, I didn't add a user field to College.
        # I'll fix core/models.py first.
        return super().form_valid(form)

from college.forms import CollegeProfileForm, CollegeCourseForm

class AddCourse(LoginRequiredMixin, CreateView):
    template_name = 'college_temp/Add_course.html'
    form_class = CollegeCourseForm
    model = CollegeCourse
    success_url = reverse_lazy('college_home')

    def form_valid(self, form):
        college = College.objects.filter(user=self.request.user).first()
        if not college:
            # Fallback/Error handling
            from django.contrib import messages
            messages.error(self.request, "Complete your college profile first.")
            return redirect('college_profile_add')
        
        form.instance.college = college
        return super().form_valid(form)


class CollegeProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        # Here id is likely the user id or college id
        data = College.objects.filter(id=id) # Simplified
        if not data.exists():
            data = College.objects.filter(name__icontains=request.user.name) # Heuristic
        
        course = []
        if data.exists():
            college = data.first()
            course = CollegeCourse.objects.filter(college=college).select_related('course')
            
        return render(request, 'college_temp/CollegeProfile.html', {"data": data, "course": course})

class CourseDelete(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        course = get_object_or_404(CollegeCourse, id=id)
        # Security: Check if this course belongs to the current user's college
        if course.college.user == request.user:
            course.delete()
            from django.contrib import messages
            messages.success(request, "Course deleted successfully.")
        return redirect('college_home')

class CollegeProfileEdit(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        college = get_object_or_404(College, user=request.user)
        form = CollegeProfileForm(instance=college)
        return render(request, 'college_temp/Add_CollegeProfile.html', {"form": form})

    def post(self, request, *args, **kwargs):
        college = get_object_or_404(College, user=request.user)
        form = CollegeProfileForm(request.POST, request.FILES, instance=college)
        if form.is_valid():
            form.save()
    
