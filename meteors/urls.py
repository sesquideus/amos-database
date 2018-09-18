from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',                              views.listMeteors,          name = 'list-meteors'),
    url(r'^list-meteors/?',                 views.listMeteors,          name = 'list-meteors'),
    url(r'^list-sightings/?',               views.listSightings,        name = 'list-sightings'),
    url(r'^sighting/(?P<sightingid>\w+)',   views.sighting,             name = 'sighting'),
    url(r'^meteor/(?P<meteorid>\w+)/path',  views.meteorKML,            name = 'meteorKML'),
    url(r'^meteor/(?P<meteorid>\w+)',       views.meteor,               name = 'meteor'),
]


