from django.urls import path
from .views import meteor, sighting, frame, snapshot


urlpatterns = [
    # Meteor listings
    path('meteors/',                                                meteor.ListDateView.as_view(),              name='list-meteors'),
    path('meteors/<slug:subnetwork_code>/',                         meteor.ListBySubnetworkView.as_view(),      name='list-meteors-by-subnetwork'),
    path('meteors/json',                                            meteor.listJSON,                            name='list-meteors-JSON'),

    # Single meteor views
    path('meteor/<slug:name>/',                                     meteor.DetailView.as_view(),                name='meteor'),
    path('meteor/<slug:name>/json',                                 meteor.DetailViewJSON.as_view(),            name='meteor-JSON'),
    path('meteor/<slug:name>/path',                                 meteor.singleKML,                           name='meteor-KML'),

    path('meteor/<slug:meteor>/<int:order>',                        snapshot.DetailView.as_view(),              name='snapshot'),

    # Sighting listings
    path('sightings/',                                              sighting.ListDateView.as_view(),            name='list-sightings'),
    path('sightings/<slug:station_code>/',                          sighting.ListByStationView.as_view(),       name='list-sightings-by-station'),
    path('sightings/latest/<int:limit>',                            sighting.ListLatestView.as_view(),          name='list-sightings-latest'),

    # Single sighting views
    path('sighting/<slug:id>/',                                     sighting.DetailView.as_view(),              name='sighting'),
    path('sighting/<slug:id>/light-curve',                          sighting.LightCurveView.as_view(),          name='sighting-light-curve'),
    path('sighting/<slug:id>/sky',                                  sighting.SkyView.as_view(),                 name='sighting-sky'),

    # Single sighting frame views
    path('sighting/<slug:sighting>/<int:order>',                    frame.DetailView.as_view(),                 name='frame'),
]
