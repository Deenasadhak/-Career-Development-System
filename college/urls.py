from django.urls import path
from college import views

urlpatterns=[
    path('dashboard/', views.CollegeHome.as_view(), name="college_dashboard"),
    path('college_profileadd/',views.CollegeProfileAdd.as_view(),name="college_ProfileAdd"),
    path('college_courseadd/',views.AddCourse.as_view(),name="course_Add"),
    path('college_profile/<int:pk>/',views.CollegeProfileView.as_view(),name="CProfile_view"),
    path('college_profiledit/<int:pk>/',views.CollegeProfileEdit.as_view(),name="CProfile_edit"),
    path('course_delete/<int:pk>/',views.CourseDelete.as_view(),name="Course_delete"),
]