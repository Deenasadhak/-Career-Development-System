from django.urls import path
from Student import views


urlpatterns=[
    path('Studenthome/',views.StudentHome.as_view(),name='Stud_home'),
    path('Student_profile/',views.Stud_AddProfile.as_view(),name='Stud_Aprofile'),
    path('profile_view/<int:pk>/',views.Stud_profileView.as_view(),name='profile_view'),
    path('profile_edit/<int:pk>/',views.Stud_profileEdit.as_view(),name='Sprofile_edit'),
    path('collegeview/',views.CollegeView.as_view(),name='college_view'),
    path('course_view/<int:pk>/',views.CourseView.as_view(),name='course_view'),
    path('aptitude/',views.AptitudeTestView.as_view(),name='take_aptitude'),
    path('filterd_college/<int:pk>/',views.Collegelist_Mark.as_view(),name='filterd_college'),

]