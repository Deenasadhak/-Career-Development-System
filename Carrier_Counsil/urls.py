"""Carrier_Counsil URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

from django.conf import settings
from django.conf.urls.static import static

from CarrierApp import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('student/',include("Student.urls")),
    path('college/',include("college.urls")),
    path('super/',include("Admin.urls")),


    path('',views.Home.as_view(),name="home"),
    path('User_reg/',views.UserRegistration.as_view(),name="U_reg"),
    path('login/',views.LoginView.as_view(),name="login"),
    path('logout/',views.Logout.as_view(),name="logout"),
    path('colle_list/',views.CollegeView.as_view(),name="col_list"),
    path('cour_list/<int:pk>/',views.CourseView.as_view(),name="cour_list"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

