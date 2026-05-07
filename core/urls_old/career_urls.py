from django.urls import path
from core.views import career_views as views

app_name = 'careers'

urlpatterns = [
    path('', views.CareerListView.as_view(), name='list'),
    path('gulf/', views.GulfCareersView.as_view(), name='gulf'),
    path('category/<slug:slug>/', views.CareerCategoryView.as_view(), name='category'),
    path('<slug:slug>/', views.CareerDetailView.as_view(), name='detail'),
]
