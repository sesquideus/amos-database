from django.urls import include, path
from . import views

urlpatterns = [
    path('',                            views.listMeteors,          name = 'list-meteors'),
    path('meteors',                     views.listMeteors,          name = 'list-meteors'),
    path('sightings',                   views.listSightings,        name = 'list-sightings'),
    path('sighting/<slug:id>',          views.sighting,             name = 'sighting'),
    #path('meteor/<slug:meteorid>',      views.meteorKML,            name = 'meteorKML'),
    path('meteor/<slug:id>/path',       views.meteor,               name = 'meteor'),
]
