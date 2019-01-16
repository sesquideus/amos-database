from django.urls import include, path
from . import views

urlpatterns = [
    path('',                            views.listMeteors,          name = 'listMeteors'),
    path('meteor/<slug:id>',            views.meteor,               name = 'meteor'),
    path('meteor/<slug:id>/path',       views.meteorKML,            name = 'meteorKML'),
    path('sightings',                   views.listSightings,        name = 'listSightings'),
    path('sighting/<slug:id>',          views.sighting,             name = 'sighting'),
]
