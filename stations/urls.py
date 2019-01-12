from django.urls import include, path
from . import views

urlpatterns = [
    path('',                            views.status,   name = 'status'),
    path('station/<slug:code>',         views.station,  name = 'station'),
]
