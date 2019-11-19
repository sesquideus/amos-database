from django.urls import path
from .views import meteor, sighting, frame

urlpatterns = [
    # Meteor listings
    path('meteors/',                                meteor.ListDateView.as_view(),          name = 'list-meteors'),
    path('meteors/json',                            meteor.listJSON,                        name = 'list-meteors-JSON'),

    # Sighting listings
    path('sightings/',                              sighting.ListDateView.as_view(),        name = 'list-sightings'),
    path('sightings/<slug:stationCode>/',           sighting.ListByStationView.as_view(),   name = 'list-sightings-by-station'),

    # Single meteor views
    path('meteor/<slug:name>/',                     meteor.SingleView.as_view(),            name = 'meteor'),
    path('meteor/<slug:name>/json',                 meteor.SingleViewJSON.as_view(),        name = 'meteor-JSON'),
    path('meteor/<int:id>/path',                    meteor.singleKML,                       name = 'meteor-KML'),

    # Single sighting views
    path('sighting/<slug:id>/',                     sighting.SingleView.as_view(),          name = 'sighting'),
    path('sighting/<slug:id>/light-curve',          sighting.light_curve,                   name = 'sighting-light-curve'),
    path('sighting/<slug:sighting>/<int:order>',    frame.SingleView.as_view(),             name = 'frame'),
]
