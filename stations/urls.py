from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from .views import station, subnetwork, heartbeat

urlpatterns = [
    path('',                                subnetwork.StatusView.as_view(),    name='status'),
    path('stations/',                       subnetwork.StatusView.as_view(),    name='status'),

    path('station/<slug:code>/',            station.DetailView.as_view(),       name='station'),
    path('station/<slug:code>/json/',       station.DetailViewJSON.as_view(),   name='station-JSON'),
    path('station/<slug:code>/heartbeat/',  station.APIViewHeartbeat.as_view(), name='station-receive-heartbeat'),
    path('station/<slug:code>/sighting/',   station.APIViewSighting.as_view(),  name='station-receive-sighting'),
    path('stations/json/',                  station.ListViewJSON.as_view(),     name='list-stations-JSON'),

    path('subnetwork/<slug:code>/',         subnetwork.SingleView.as_view(),    name='subnetwork'),

    path('station/<slug:code>/<slug:id>/',  heartbeat.SingleView.as_view(),     name='heartbeat'),
]
