from django.urls import path
from Admin import views

urlpatterns=[
    path('super_home/',views.AdminHome.as_view(),name="super_home"),
    path('student_list/',views.StudentList.as_view(),name="student_list"),
    path('student_delete/<int:pk>/',views.StudentDelete.as_view(),name="student_delete"),
    path('college_list/',views.CollegeList.as_view(),name="college_list"),
    path('college_delete/<int:pk>/',views.CollegeDelete.as_view(),name="college_delete"),
    path('Add_question/',views.AddQuestion.as_view(),name="Add_question"),
    path('Add_answer/',views.AddAnswer.as_view(),name="Add_answer"),
    path('question_view/',views.Questionlist.as_view(),name="Q_view"),
    path('question_delete/<int:pk>/',views.QuestionDelete.as_view(),name="Q_dele"),
     path('acourse_view/<int:pk>/',views.ACourseView.as_view(),name='Acourse_view'),

]