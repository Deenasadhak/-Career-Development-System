from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import RedirectView

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('CarrierApp.urls')),
    path('student/', include('Student.urls')),
    # Legacy redirects
    path('home/', RedirectView.as_view(pattern_name='landing', permanent=True)),
    path('student/<path:extra>', RedirectView.as_view(pattern_name='explore', permanent=True)),
    path('college/<path:extra>', RedirectView.as_view(pattern_name='explore', permanent=True)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


