from django.shortcuts import render,redirect
from django.views.generic import TemplateView,View,CreateView,FormView
from CarrierApp.models import Student,College,Course,Login,Question,Answer
from Admin.forms import AnswerForm,QuestionForm
from django.urls import reverse_lazy

# Create your views here.

class AdminHome(TemplateView):
    template_name='Admin_temp/index.html'

class StudentList(View):
    def get(self,request):
        data=Student.objects.all()
        return render(request,'Admin_temp/studentlist.html',{"data":data})
class StudentDelete(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')   
        student_instance = Student.objects.get(id=id)
        user_instance = student_instance.user
        student_instance.delete()
        user_instance.delete()
        return redirect('student_list') 
    
class CollegeList(View):
    def get(self,request):
        data=College.objects.all()
        return render(request,'Admin_temp/collegelist.html',{"data":data})
class CollegeDelete(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')   
        college_instance = College.objects.get(id=id)
        user_instance = college_instance.user

        # Delete the College instance and its associated Login instance
        college_instance.delete()
        user_instance.delete()
        return redirect('college_list')
    
class AddQuestion(CreateView):
    template_name='Admin_temp/Add_questions.html'  
    form_class=QuestionForm
    model=Question
    success_url=reverse_lazy('Add_question') 

class AddAnswer(FormView):
    template_name='Admin_temp/Add_answer.html'  
    form_class=AnswerForm
    # model=Answer
    # success_url=reverse_lazy('Add_answer')  
    def post(self,request):
        form=AnswerForm(request.POST)
        if form.is_valid():
            Answer.objects.create(**form.cleaned_data) 
        else:
            print("invalid")
        return redirect('Add_answer')        
      
class Questionlist(View):
    def get(self,request):
        data=Question.objects.all()
        return render(request,'Admin_temp/Questionlist.html',{"data":data})
    
class QuestionDelete(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')    
        Question.objects.get(id=id).delete()
        return redirect('Q_view')
    
class ACourseView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        data=Course.objects.filter(College_name=id)
        return render(request,'Admin_temp/course.html',{"data":data})    

          

             




