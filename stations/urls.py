from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from .views import station, subnetwork

urlpatterns = [
    path('',                                subnetwork.StatusView.as_view(),    name = 'status'),
    path('stations/',                       subnetwork.StatusView.as_view(),    name = 'status'),

    path('station/<slug:code>/',            station.SingleView.as_view(),       name = 'station'),
    path('station/<slug:code>/json/',       station.SingleViewJSON.as_view(),   name = 'station-JSON'),
    path('station/<slug:code>/status/',     station.APIView.as_view(),          name = 'station-add-status'),
    path('station/<slug:code>/sighting/',   station.APIViewSighting.as_view(),  name = 'station-add-sighting'),
    path('stations/json/',                  station.ListViewJSON.as_view(),     name = 'list-stations-JSON'),

    path('subnetwork/<slug:code>/',         subnetwork.SingleView.as_view(),    name = 'subnetwork'),
]
