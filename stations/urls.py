from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from .views import station, subnetwork

urlpatterns = [
    path('',                            station.status,                     name = 'status'),
    path('stations',                    station.status,                     name = 'status'),
    path('station/<slug:code>/',        station.SingleView.as_view(),       name = 'station'),
    path('station/<slug:code>/json/',   station.JSONView.as_view(),         name = 'stationJSON'),
    path('station/status-update/',      csrf_exempt(station.process),          name = 'statusUpdate'),

    path('subnetwork/<slug:code>/',     subnetwork.SingleView.as_view(),    name = 'subnetwork'),
]
