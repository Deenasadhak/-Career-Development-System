from django.shortcuts import render,redirect
from django.views.generic import TemplateView,CreateView,View,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from college.forms import CollegeProfileForm,AddCourseForm
from django.urls import reverse_lazy
from CarrierApp.models import College,Course
# Create your views here.

class CollegeHome(TemplateView):
    template_name='college_temp/index.html'

class CollegeProfileAdd(LoginRequiredMixin,CreateView):
    template_name='college_temp/Add_CollegeProfile.html'   
    form_class=CollegeProfileForm
    model=College
    success_url=reverse_lazy('college_home')

    def form_valid(self, form):
        form.instance.user=self.request.user
        return super().form_valid(form)
    
class AddCourse(CreateView):
    template_name='college_temp/Add_course.html'
    form_class=AddCourseForm
    model=Course
    success_url=reverse_lazy('course_Add')

    def form_valid(self, form):
        form.instance.College_name=self.request.user.college_profile
        return super().form_valid(form)
from django.http import Http404

class CollegeProfileView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        data=College.objects.filter(user=id)
        for i in data:
            course=Course.objects.filter(College_name=i.id)
        return render(request,'college_temp/CollegeProfile.html',{"data":data,"course":course})
    
class CourseDelete(View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        data=Course.objects.get(id=id)
        data.delete()
        return redirect('college_home')

     
    
class CollegeProfileEdit(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        data=College.objects.get(user=id)
        form=CollegeProfileForm(instance=data)
        return render(request,'college_temp/Add_CollegeProfile.html',{"form":form})
    def post(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        data=College.objects.get(user=id)
        form=CollegeProfileForm(request.POST,instance=data)
        if form.is_valid():
            form.save()
        else:
            print("invalid")
        return redirect('college_home')  
    
    
     



    
