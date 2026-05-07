from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from Admin.forms import QuestionWithChoicesForm
from CarrierApp.models import Student, Mark, Question, Answer, Login
from core.models import College, Course, CollegeCourse
from django.utils import timezone
from django.contrib import messages

class AdminHome(LoginRequiredMixin, TemplateView):
    template_name = 'Admin_temp/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from core.models import College
        from Student.models import Student
        from CarrierApp.models import Question
        
        context['college_count'] = College.objects.count()
        context['student_count'] = Student.objects.count()
        context['question_count'] = Question.objects.count()
        context['visitors_count'] = 1294 # Demo static
        
        # Monthly statistics for Chart.js
        from django.db.models.functions import ExtractMonth
        from django.db.models import Count
        monthly_stats = Mark.objects.annotate(month=ExtractMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')
        
        # Convert to list for Chart.js
        stats_list = [0] * 12
        for s in monthly_stats:
            if s['month']:
                stats_list[s['month']-1] = s['count']
        context['monthly_stats'] = stats_list

        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        context['assessments_today'] = Mark.objects.filter(created_at__gte=today_start).count()
        context['recent_registrations'] = Login.objects.order_by('-id')[:5]
        return context

class StudentList(LoginRequiredMixin, View):
    def get(self, request):
        students = Student.objects.all().select_related('user')
        return render(request, 'Admin_temp/studentlist.html', {"data": students})

class StudentDelete(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        student = get_object_or_404(Student, id=id)
        user = student.user
        student.delete()
        if user:
            user.delete()
        return redirect('student_list')

class CollegeList(LoginRequiredMixin, View):
    def get(self, request):
        colleges = College.objects.all()
        return render(request, 'Admin_temp/collegelist.html', {"data": colleges})

class CollegeDelete(View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        College.objects.filter(id=id).delete()
        return redirect('college_list')

class UserToggleStatus(LoginRequiredMixin, View):
    def get(self, request, pk):
        user_obj = get_object_or_404(Login, id=pk)
        user_obj.is_active = not user_obj.is_active
        user_obj.save()
        status = "activated" if user_obj.is_active else "deactivated"
        messages.success(request, f"User {user_obj.username} has been {status}.")
        return redirect(request.META.get('HTTP_REFERER', 'super_home'))

class AddQuestion(LoginRequiredMixin, CreateView):
    template_name = 'Admin_temp/Add_questions.html'
    form_class = QuestionWithChoicesForm
    model = Question
    success_url = reverse_lazy('Q_view')

    def form_valid(self, form):
        question = form.save()
        options_data = [
            ('A', form.cleaned_data['option_a']),
            ('B', form.cleaned_data['option_b']),
            ('C', form.cleaned_data['option_c']),
            ('D', form.cleaned_data['option_d']),
        ]
        correct_key = form.cleaned_data['correct_option']
        
        for key, text in options_data:
            Answer.objects.create(
                question=question,
                answer=text,
                is_correct=(key == correct_key)
            )
        messages.success(self.request, "Question and options added successfully.")
        return redirect(self.success_url)

class Questionlist(LoginRequiredMixin, View):
    def get(self, request):
        category = request.GET.get('category')
        questions = Question.objects.all()
        if category:
            questions = questions.filter(category=category)
        
        categories = [c[0] for c in Question.CATEGORY_CHOICES]
        return render(request, 'Admin_temp/Questionlist.html', {
            "data": questions,
            "categories": categories,
            "selected_category": category
        })

class QuestionDelete(View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        Question.objects.filter(id=id).delete()
        return redirect('Q_view')

class ACourseView(View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        data = CollegeCourse.objects.filter(college_id=id).select_related('course')
        return render(request, 'Admin_temp/course.html', {"data": data})
