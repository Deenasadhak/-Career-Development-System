from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('explore/', views.explore_view, name='explore'),
    path('recommend/', views.recommend_view, name='recommend'),
    path('careers/', views.careers_view, name='careers'),
    path('generate-roadmap/<int:career_id>/', views.generate_roadmap_view, name='generate_roadmap'),
]



