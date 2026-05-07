from django.urls import path
from Student import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='student_dashboard'),
    path('profile/', views.profile_view, name='student_profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('assessment/', views.assessment_view, name='student_assessment'),
    path('results/', views.results_view, name='student_results'),
    path('course-guidance/', views.course_guidance_view, name='course_guidance'),
    path('college-discovery/', views.college_discovery_view, name='college_discovery'),
    path('career-guidance/', views.career_guidance_view, name='career_guidance'),
    path('assessment/retake/', views.retake_assessment_view, name='retake_assessment'),
    path('explore-career-ajax/', views.explore_career_ajax, name='explore_career_ajax'),
]