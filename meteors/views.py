from django.shortcuts import render

from .models import Meteor, Sighting

# Create your views here.

def listMeteors(request):
    context = {
        'meteors': Meteor.objects.all(),
    }
    return render(request, 'list-meteors.html', context)

def listSightings(request):
    context = {
        'sightings': Sighting.objects.all(),
    }
    return render(request, 'list-sightings.html', context)

def meteor(request, meteorid):
    context = {
        'meteor': Meteor.objects.get(id = meteorid)
    }        
    return render(request, 'meteor.html', context)

def sighting(request, sightingid):
    sighting = Sighting.objects.get(id = sightingid)
    loc = AltAz(obstime = Time(sighting.lightmaxTime), location = sighting.location.earthLocation())
    moon = get_moon(Time(sighting.lightmaxTime), sighting.location.earthLocation()).transform_to(loc)
    context = {
        'sighting': Sighting.objects.get(id = sightingid),
        'moon': {
            'coord': moon,
            'elong': moon.separation(sighting.skyCoord()),
        }
    }
    return render(request, 'sighting.html', context)
