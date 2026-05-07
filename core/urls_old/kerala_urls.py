from django.urls import path
from core.views.kerala_views import (
    CAPGuidanceView, PSCOpportunitiesView, PSCPostDetailView,
    GulfOpportunitiesView, GulfCountryDetailView,
    AyurvedaPathwaysView, TourismPathwaysView
)

app_name = 'kerala'

urlpatterns = [
    # CAP
    path('cap/guidance/', CAPGuidanceView.as_view(), name='cap_guidance'),

    # PSC
    path('psc/', PSCOpportunitiesView.as_view(), name='psc_list'),
    path('psc/<int:pk>/<slug:slug>/', PSCPostDetailView.as_view(), name='psc_detail'),

    # Gulf
    path('gulf/', GulfOpportunitiesView.as_view(), name='gulf_list'),
    path('gulf/<slug:slug>/', GulfCountryDetailView.as_view(), name='gulf_country'),

    # Special pathways
    path('ayurveda/', AyurvedaPathwaysView.as_view(), name='ayurveda'),
    path('tourism/', TourismPathwaysView.as_view(), name='tourism'),
]
