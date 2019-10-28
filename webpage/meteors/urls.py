from django.urls import path
from .views import meteor, sighting, frame

urlpatterns = [

    # Meteor listings
    path('meteors/',                                meteor.ListDateView.as_view(),          name = 'listMeteors'),
    path('meteors/json',                            meteor.listJSON,                        name = 'listMeteorsJSON'),

    # Sighting listings
    path('sightings/',                              sighting.ListDateView.as_view(),        name = 'listSightings'),
    path('sightings/<slug:stationCode>/',           sighting.ListByStationView.as_view(),   name = 'listSightingsByStation'),

    # Single meteor views
    path('meteor/<slug:name>/',                     meteor.SingleView.as_view(),            name = 'meteor'),
    path('meteor/<slug:name>/json',                 meteor.SingleViewJSON.as_view(),        name = 'meteorJSON'),
    path('meteor/<int:id>/path',                    meteor.singleKML,                       name = 'meteorKML'),

    # Single sighting views
    path('sighting/<slug:id>/',                     sighting.SingleView.as_view(),          name = 'sighting'),
    path('sighting/<slug:id>/light-curve',          sighting.lightCurve,                    name = 'sightingLightCurve'),
    path('sighting/<slug:sighting>/<int:order>',    frame.SingleView.as_view(),             name = 'frame'),

    # API views, to be tidied up
    path('meteor/receive',                          meteor.APIView.as_view(),               name = 'receive'),
]
