import datetime
from django.shortcuts import render

from . import models

# Create your views here.

def status(request):
    context = {
        'subnetworks': models.Subnetwork.objects.all(),
    }
    return render(request, 'stations/status.html', context)

def station(request, code):
    station = models.Station.objects.get(code = code)

    context = {
        'station': station,
        'lastDay': station.sighting_set.filter(lightmaxTime__gte = datetime.datetime.now() - datetime.timedelta(days = 1))
    }
    return render(request, 'stations/station.html', context)

