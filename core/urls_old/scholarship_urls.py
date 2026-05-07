from django.urls import path
from core.views import career_views as views

app_name = 'scholarships'

urlpatterns = [
    path('', views.ScholarshipListView.as_view(), name='list'),
    path('eligible/', views.EligibleScholarshipsView.as_view(), name='eligible'),
]
