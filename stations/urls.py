from django.urls import include, path
from . import views

urlpatterns = [
    path('',                            views.status,       name = 'status'),
    path('<slug:code>/',                views.station,      name = 'station'),
    path('json',                        views.stationsJSON, name = 'stationsJSON'),
]
