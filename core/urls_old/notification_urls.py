from django.urls import path
from core.views.notification_views import (
    NotificationListView, NotificationCountView, MarkAllReadView,
    NotificationPreferenceView, MarkReadView
)

app_name = 'notifications'

urlpatterns = [
    path('',
         NotificationListView.as_view(),
         name='list'),
    path('count/',
         NotificationCountView.as_view(),
         name='count'),
    path('read-all/',
         MarkAllReadView.as_view(),
         name='read_all'),
    path('preferences/',
         NotificationPreferenceView.as_view(),
         name='preferences'),
    path('<int:pk>/read/',
         MarkReadView.as_view(),
         name='mark_read'),
]
