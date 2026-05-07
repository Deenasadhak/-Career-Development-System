from django.urls import path
from core.views.admin_views import (
    SuperAdminDashboardView, StudentManagementView, StudentExportView,
    CollegeManagementView, CollegeVerifyView,
    QuestionManagementView, QuestionBulkActivateView
)

app_name = 'admin_dashboard'

urlpatterns = [
    path('', SuperAdminDashboardView.as_view(), name='dashboard'),
    path('students/export/', StudentExportView.as_view(), name='students_export'),
    path('students/', StudentManagementView.as_view(), name='students'),
    path('colleges/', CollegeManagementView.as_view(), name='colleges'),
    path('colleges/<int:pk>/verify/', CollegeVerifyView.as_view(), name='college_verify'),
    path('questions/', QuestionManagementView.as_view(), name='questions'),
    path('questions/bulk-action/', QuestionBulkActivateView.as_view(), name='questions_bulk'),
]
