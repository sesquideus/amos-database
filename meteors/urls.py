import datetime

from django.urls import include, path
from . import views

urlpatterns = [
    path('json',                            views.listMeteorsJSON,      name = 'listMeteorsJSON'),

    # Meteor listings
    path('meteors/',                        views.listMeteors,          name = 'listMeteors'),

    # Sighting listings
    path('sightings/',                      views.listSightings,        name = 'listSightings'),
    path('sightings/<slug:stationCode>',    views.listSightingsStation, name = 'listSightingsStation'),

    # Single meteor views
    path('meteor/<slug:id>/',               views.meteor,               name = 'meteor'),
    path('meteor/<slug:id>/json',           views.meteorJSON,           name = 'meteorJSON'),
    path('meteor/<slug:id>/path',           views.meteorKML,            name = 'meteorKML'),

    # Single sighting views
    path('sighting/<slug:id>',              views.sighting,             name = 'sighting'),


    path('create',                          views.createRandom,         name = 'createRandom'),
]
