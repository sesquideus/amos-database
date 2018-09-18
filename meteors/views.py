from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from astropy.coordinates import EarthLocation, AltAz, get_sun, get_moon
from astropy.time import Time
from datetime import datetime
from .models import Sighting, Meteor

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

def meteorKML(request, meteorid):
    meteor = Meteor.objects.get(id = meteorid)
    context = {
        'meteor': meteor,
    }
    response = HttpResponse(render(request, 'meteorKML.kml', context), content_type = "application/vnd.google-earth.kml+xml")
    response['Content-Disposition'] = 'attachment; filename="{id}.kml"'.format(id = meteor.id)
    return response
