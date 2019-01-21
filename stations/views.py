import datetime
from django.shortcuts import render
from django.http import JsonResponse

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

def stationsJSON(request):
    stations = {}
    for station in models.Station.objects.all():
        stations[station.id] = station.asDict()

    return JsonResponse(stations)

