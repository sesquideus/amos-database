import datetime

from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime, parse_date

from astropy.time import Time
from astropy.coordinates import AltAz, get_moon, get_sun

from .models import Meteor, Sighting
from stations.models import Station

def parseDatetime(string, default = datetime.datetime.now()):
    return parse_datetime(string) if string else default

# Create your views here.

@login_required
def listMeteors(request):
    context = {
        'meteors': Meteor.objects.all(),
    }
    return render(request, 'meteors/list-meteors.html', context)

@login_required
def listMeteorsJSON(request):
    meteors = {}
    for meteor in Meteor.objects.all():
        meteors[meteor.id] = meteor.asDict()

    return JsonResponse(meteors)

@login_required
def listSightings(request):
    timeFrom = parseDatetime(request.GET.get('from'), datetime.datetime(1970, 1, 1))
    timeTo = parseDatetime(request.GET.get('to'), datetime.datetime.now())

    context = {
        'sightings': Sighting.objects.filter(lightmaxTime__gte = timeFrom, lightmaxTime__lte = timeTo),
    }
    return render(request, 'meteors/list-sightings.html', context)

@login_required
def listSightingsNight(request, date):
    midnight = parse_date(date)
    timeFrom = midnight + datetime.timedelta(days = -0.5)
    timeTo   = midnight + datetime.timedelta(days = 0.5)
    context = {
        'sightings': Sighting.objects.filter(lightmaxTime__gte = timeFrom, lightmaxTime__lte = timeTo),
    }
    return render(request, 'meteors/list-sightings.html', context)

@login_required
def listSightingsStation(request, stationCode):
    midnight = datetime.datetime.combine(parse_date(request.GET.get('date', datetime.date.today().isoformat())), datetime.time())
    timeFrom = midnight + datetime.timedelta(days = -0.5)
    timeTo   = midnight + datetime.timedelta(days = 0.5)

    context = {
        'date': midnight,
        'timeFrom': timeFrom,
        'timeTo': timeTo,
        'station': Station.objects.get(code = stationCode),
        'sightings': Sighting.objects.filter(lightmaxTime__gte = timeFrom, lightmaxTime__lte = timeTo, station__code = stationCode),
    }
    return render(request, 'meteors/list-sightings.html', context)
    

@login_required
def meteor(request, id):
    print("OK")
    context = {
        'meteor': Meteor.objects.get(id = id)
    }        
    return render(request, 'meteors/meteor.html', context)

@login_required
def meteorJSON(request, id):
    meteor = Meteor.objects.get(id = id)
    data = serializers.serialize('json', meteor)
    return JsonResponse(data, safe = False)

@login_required
def meteorKML(request, id):
    context = {
        'meteor': Meteor.objects.get(id = id)
    }
    return render(request, 'meteors/meteor.kml', context)

@login_required
def sighting(request, id):
    sighting = Sighting.objects.get(id = id)
    loc = AltAz(obstime = Time(sighting.lightmaxTime), location = sighting.station.earthLocation())
    moon = get_moon(Time(sighting.lightmaxTime), sighting.station.earthLocation()).transform_to(loc)
    sun = get_sun(Time(sighting.lightmaxTime)).transform_to(loc)
    context = {
        'sighting': Sighting.objects.get(id = id),
        'moon': sighting.getMoonInfo(),
        'sun': sighting.getSunInfo(),
    }
    return render(request, 'meteors/sighting.html', context)

@login_required
def createRandom(request):
    meteor = Meteor.objects.createRandom()
    meteor.save()
    return render(request, 'meteors/meteor.kml', {}) 
