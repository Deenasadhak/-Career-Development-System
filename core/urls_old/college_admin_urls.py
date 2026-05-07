from django.urls import path
from core.views.admin_views import (
    CollegeAdminDashboardView, CollegeProfileUpdateView,
    CollegeCourseManagementView, CollegeCourseUpdateView
)

app_name = 'college_admin'

urlpatterns = [
    path('dashboard/', CollegeAdminDashboardView.as_view(), name='dashboard'),
    path('profile/', CollegeProfileUpdateView.as_view(), name='profile'),
    path('courses/', CollegeCourseManagementView.as_view(), name='courses'),
    path('courses/<int:pk>/update/', CollegeCourseUpdateView.as_view(), name='course_update'),
]
