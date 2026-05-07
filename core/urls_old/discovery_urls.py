from django.urls import path
from core.views.discovery_views import (
    StreamListView, StreamDetailView,
    CollegeListView, CollegeDetailView, CompareCollegesView,
    CourseListView, CourseDetailView, CompareCoursesView,
    QuickSearchView
)

app_name = 'discovery'

urlpatterns = [
    # Streams
    path('streams/', StreamListView.as_view(), name='stream_list'),
    path('streams/<slug:slug>/', StreamDetailView.as_view(), name='stream_detail'),

    # Colleges
    path('colleges/', CollegeListView.as_view(), name='college_list'),
    path('colleges/compare/', CompareCollegesView.as_view(), name='compare_colleges'),
    path('colleges/<slug:slug>/', CollegeDetailView.as_view(), name='college_detail'),

    # Courses
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/compare/', CompareCoursesView.as_view(), name='compare_courses'),
    path('courses/<slug:slug>/', CourseDetailView.as_view(), name='course_detail'),

    # Global search
    path('search/', QuickSearchView.as_view(), name='search'),
]
