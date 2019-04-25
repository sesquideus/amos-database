import datetime
import pytz
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required

from . import models

# Create your views here.

@login_required
def status(request):
    context = {
        'subnetworks': models.Subnetwork.objects.all(),
    }
    return render(request, 'stations/status.html', context)

def station(request, code):
    station = models.Station.objects.get(code = code)

    context = {
        'station': station,
        'lastDay': station.sighting_set.filter(timestamp__gte = datetime.datetime.now(pytz.utc) - datetime.timedelta(days = 1))
    }
    return render(request, 'stations/station.html', context)

def stationsJSON(request):
    return JsonResponse({station.id: station.asDict() for station in models.Station.objects.all()})
