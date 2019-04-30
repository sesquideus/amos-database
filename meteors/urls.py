from django.urls import path
from .views import meteor, sighting, frame

urlpatterns = [
    path('meteors/json',                            meteor.listJSON,                        name = 'listMeteorsJSON'),

    # Meteor listings
    path('meteors/',                                meteor.ListView.as_view(),              name = 'listMeteors'),

    # Sighting listings
    path('sightings/',                              sighting.ListView.as_view(),            name = 'listSightings'),
    path('sightings/<slug:stationCode>/',           sighting.ListByStationView.as_view(),   name = 'listSightingsStation'),

    # Single meteor views
    path('meteor/<slug:name>/',                     meteor.SingleView.as_view(),            name = 'meteor'),
    path('meteor/<int:id>/json',                    meteor.singleJSON,                      name = 'meteorJSON'),
    path('meteor/<int:id>/path',                    meteor.singleKML,                       name = 'meteorKML'),

    # Single sighting views
    path('sighting/<slug:id>/',                     sighting.SingleView.as_view(),          name = 'sighting'),
    path('sighting/<slug:id>/chart',                sighting.chart,                         name = 'sightingChart'),
    path('sighting/<slug:sighting>/<int:order>',    frame.single,                           name = 'frame'),

    # API views, to be tidied up
    path('meteor/receive',                          meteor.APIView.as_view(),               name = 'receive'),
]
