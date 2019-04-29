from django.urls import path
from .views import meteor, sighting, frame

urlpatterns = [
    path('meteors/json',                            meteor.listJSON,                    name = 'listMeteorsJSON'),

    # Meteor listings
    path('meteors/',                                meteor.ListView.as_view(),          name = 'listMeteors'),

    # Sighting listings
    path('sightings/',                              sighting.ListView.as_view(),        name = 'listSightings'),
    path('sightings/<slug:stationCode>/',           views.listSightingsStation,         name = 'listSightingsStation'),

    # Single meteor views
    path('meteor/<slug:name>/',                     views.MeteorView.as_view(),         name = 'meteor'),
    path('meteor/<int:id>/json',                    views.meteorJSON,                   name = 'meteorJSON'),
    path('meteor/<int:id>/path',                    views.meteorKML,                    name = 'meteorKML'),

    # Single sighting views
    path('sighting/<slug:id>/',                     views.sighting,                     name = 'sighting'),
    path('sighting/<slug:id>/chart',                views.sightingChart,                name = 'sightingChart'),
    path('sighting/<slug:sighting>/<int:order>',    views.frame,                        name = 'frame'),

    # API views, to be tidied up
    path('meteor/random',                           views.createRandom,                 name = 'createRandom'),
    path('meteor/receive',                          views.MeteorAPIView.as_view(),      name = 'receive'),
]
