from django.urls import path
from core.views import career_views as views

app_name = 'exams'

urlpatterns = [
    path('', views.EntranceExamListView.as_view(), name='list'),
    path('<int:pk>/', views.EntranceExamDetailView.as_view(), name='detail'),
]
