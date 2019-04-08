from django.urls import path
from . import views

urlpatterns = [
    path('json',                            views.listMeteorsJSON,              name = 'listMeteorsJSON'),

    # Meteor listings
    path('meteors/',                        views.ListMeteorsView.as_view(),    name = 'listMeteors'),

    # Sighting listings
    path('sightings/',                      views.ListSightingsView.as_view(),  name = 'listSightings'),
    path('sightings/<slug:stationCode>/',   views.listSightingsStation,         name = 'listSightingsStation'),

    # Single meteor views
    path('meteor/<slug:name>/',             views.MeteorView.as_view(),         name = 'meteor'),
    path('meteor/<int:id>/json',            views.meteorJSON,                   name = 'meteorJSON'),
    path('meteor/<int:id>/path',            views.meteorKML,                    name = 'meteorKML'),

    # Single sighting views
    path('sighting/<slug:id>',              views.sighting,                     name = 'sighting'),


    path('create',                          views.createRandom,                 name = 'createRandom'),
    path('receive',                         views.MeteorAPIView.as_view(),      name = 'receive'),
]
