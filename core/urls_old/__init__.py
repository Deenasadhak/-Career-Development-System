from django.urls import path
from django.views.generic import TemplateView

app_name = 'core'

urlpatterns = [
    # Taxonomy Browsing
    path('streams/', TemplateView.as_view(template_name='core/stub.html'), name='stream_list'),
    path('streams/<slug:slug>/', TemplateView.as_view(template_name='core/stub.html'), name='stream_detail'),
    
    # College Discovery
    path('colleges/', TemplateView.as_view(template_name='core/stub.html'), name='college_list'),
    path('colleges/<slug:slug>/', TemplateView.as_view(template_name='core/stub.html'), name='college_detail'),
    
    # Course Explorer
    path('courses/', TemplateView.as_view(template_name='core/stub.html'), name='course_list'),
    path('courses/<slug:slug>/', TemplateView.as_view(template_name='core/stub.html'), name='course_detail'),
]
