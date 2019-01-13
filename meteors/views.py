from django.shortcuts import render

from astropy.time import Time
from astropy.coordinates import AltAz, get_moon

from .models import Meteor, Sighting

# Create your views here.

def listMeteors(request):
    context = {
        'meteors': Meteor.objects.all(),
    }
    return render(request, 'meteors/list-meteors.html', context)

def listSightings(request):
    context = {
        'sightings': Sighting.objects.all(),
    }
    return render(request, 'meteors/list-sightings.html', context)

def meteor(request, id):
    context = {
        'meteor': Meteor.objects.get(id = id)
    }        
    return render(request, 'meteors/meteor.html', context)

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
