from django.shortcuts import render

from . import models

# Create your views here.

def status(request):
    context = {
        'subnetworks': models.Subnetwork.objects.all(),
    }
    return render(request, 'stations/status.html', context)

def station(request, code):
    context = {
    }
    return render(request, 'stations/station.html', context)

