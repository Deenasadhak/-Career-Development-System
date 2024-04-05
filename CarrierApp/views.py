from django.shortcuts import render,redirect
from django.views.generic import TemplateView,View,CreateView,FormView
from CarrierApp.forms import Registration,LoginForm
from CarrierApp.models import Login,College,Course
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
# Create your views here.

class Home(TemplateView):
    template_name='index.html'

# class UserRegistration(View):
#     def get(self,request):
#         form=Registration()
#         return render(request,'UserRegistration.html',{"form":form})

class UserRegistration(FormView):
    template_name='UserRegistration.html'
    form_class=Registration
    def post(self,request):
        form=Registration(request.POST)
        if form.is_valid():
            Login.objects.create_user(**form.cleaned_data)
        else:
            print("invalid")
        return redirect('login')        
            

class LoginView(FormView):
    template_name='login.html'
    form_class=LoginForm

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if request.user.is_superuser:
                    request.session['user_type'] = 'superuser'
                    return redirect('super_home')
                elif request.user.is_student:
                    request.session['user_type'] = 'student'
                    return redirect('Stud_home')
                else:
                    request.session['user_type'] = 'college'
                    return redirect('college_home')
            else:
                messages.error(request,"Invalid credentials")
                
                return redirect('login')
        else:
            
            return redirect('login')      
        
class Logout(View):
    def get(self,request):
        logout(request)
        return redirect("home")   


class CollegeView(View):
    def get(self,request):
        data=College.objects.all()
        return render(request,'collegelist.html',{"data":data})  

class CourseView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        data=Course.objects.filter(College_name=id)
        return render(request,'courselist.html',{"data":data})    


      


