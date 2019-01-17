from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse

from astropy.time import Time
from astropy.coordinates import AltAz, get_moon

from .models import Meteor, Sighting

# Create your views here.

def listMeteors(request):
    context = {
        'meteors': Meteor.objects.all(),
    }
    return render(request, 'meteors/list-meteors.html', context)

def listMeteorsJSON(request):
    meteors = {}
    for meteor in Meteor.objects.all():
        meteors[meteor.id] = meteor.asDict()

    return JsonResponse(meteors)

def listSightings(request):
    context = {
        'sightings': Sighting.objects.all(),
    }
    return render(request, 'meteors/list-sightings.html', context)

def meteor(request, id):
    print("OK")
    context = {
        'meteor': Meteor.objects.get(id = id)
    }        
    return render(request, 'meteors/meteor.html', context)

def meteorJSON(request, id):
    meteor = Meteor.objects.get(id = id)
    data = serializers.serialize('json', meteor)
    return JsonResponse(data, safe = False)

def meteorKML(request, id):
    context = {
        'meteor': Meteor.objects.get(id = id)
    }
    return render(request, 'meteors/meteor.kml', context)

def sighting(request, id):
    sighting = Sighting.objects.get(id = id)
    loc = AltAz(obstime = Time(sighting.lightmaxTime), location = sighting.station.earthLocation())
    moon = get_moon(Time(sighting.lightmaxTime), sighting.station.earthLocation()).transform_to(loc)
    context = {
        'sighting': Sighting.objects.get(id = id),
        'moon': {
            'coord': moon,
            'elong': moon.separation(sighting.skyCoord()),
        }
    }
    return render(request, 'meteors/sighting.html', context)

def createRandom(request):
    meteor = Meteor.objects.createRandom()
    meteor.save()
    return render(request, 'meteors/meteor.kml', {}) 
