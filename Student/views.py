from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.generic import TemplateView,View,CreateView,UpdateView,ListView
from Student.forms import Stud_profileForm
from CarrierApp.models import Student,College,Course,Question,Answer,Mark
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class StudentHome(TemplateView):
    template_name='Stud_templates/index.html'

class Stud_AddProfile(LoginRequiredMixin,CreateView):
    template_name='Stud_templates/Add_profile.html'
    form_class=Stud_profileForm
    model=Student
    success_url=reverse_lazy('Stud_home')

    def form_valid(self, form):
        form.instance.user=self.request.user
        return super().form_valid(form)
        
class Stud_profileView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        data=Student.objects.filter(user=id)
        return render(request,'Stud_templates/profileview.html',{"data": data})
    
class Stud_profileEdit(View):
    # template_name='Stud_templates/Add_profile.html'
    # form_class=Stud_profileForm
    # model=Student
    # success_url=reverse_lazy('Stud_home')
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        data=Student.objects.get(user=id)
        form=Stud_profileForm(instance=data)  
        return render(request,'Stud_templates/Add_profile.html',{"form":form})  
    def post(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        data=Student.objects.get(user=id)
        form=Stud_profileForm(request.POST,instance=data)
        if form.is_valid():
            form.save()
        else:
            print("invalid")
        return redirect('Stud_home')     

class CollegeView(View):
    def get(self,request):
        data=College.objects.all()
        return render(request,'Stud_templates/CollegeView.html',{"data":data})
class CourseView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        data=Course.objects.filter(College_name=id)
        return render(request,'Stud_templates/CourseView.html',{"data":data})
from django.http import Http404
from django.shortcuts import get_object_or_404

class AptitudeTestView(ListView):
    model = Question
    template_name = 'Stud_templates/aptitude_test.html'
    context_object_name = 'questions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answers'] = Answer.objects.filter(question__in=context['questions'])
        student_name = self.request.user.student_profile
        try:
            mark = Mark.objects.get(student_name=student_name)
        except Mark.DoesNotExist:
            mark = None
        context['mark'] = mark
        return context

    
    
    def post(self, request, *args, **kwargs):
        total_marks = self.calculate_total_marks(request.POST)
        student_name = request.user.student_profile  # Assuming user is authenticated and has student profile
        Mark.objects.create(student_name=student_name, Mark=total_marks)
        return redirect('Stud_home')  # Redirect to a page showing the result or any other desired page

    def calculate_total_marks(self, post_data):
        total_marks = 0
        for key, value in post_data.items():
            if key.startswith('answer_'):
                answer_id = int(value)
                answer = Answer.objects.get(id=answer_id)
                if answer.is_true:
                    total_marks += 5  # Assuming each correct answer contributes 1 mark
        return total_marks
    

class Collegelist_Mark(View):
    def get(self, request, *args, **kwargs):
        student_id = kwargs.get('pk')
        student_data = Student.objects.filter(user=student_id)
        college_list = []

        for student in student_data:
            student_id = student.id
            marks = Mark.objects.filter(student_name=student_id)
            for mark in marks:
                aptitude_mark = mark.Mark
                colleges = College.objects.filter(cut_off_mark__lte=aptitude_mark)
                college_list.extend(colleges)

        # Now college_list contains all colleges with cutoff marks less than or equal to the aptitude marks
        # You can further process college_list as needed

        return render(request, 'Stud_templates/filterd_college.html', {"data": college_list})       


