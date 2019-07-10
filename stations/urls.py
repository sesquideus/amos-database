from django.urls import include, path
from .views import station, subnetwork

urlpatterns = [
    path('',                            station.status,                 name = 'status'),
    path('<slug:code>/',                station.SingleView.as_view(),   name = 'station'),
    path('json',                        station.JSONView.as_view(),     name = 'stationJSON'),
    path('status-update',               station.APIView.as_view(),      name = 'receive'),

    path('subnetwork/<slug:code>',      subnetwork.SingleView.as_view(),    name = 'subnetwork'),
]
