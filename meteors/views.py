import datetime
import pytz
from pprint import pprint as pp

from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime, parse_date
from django.utils.decorators import method_decorator

from astropy.time import Time
from astropy.coordinates import AltAz, get_moon, get_sun

from .models import Meteor, Sighting
from stations.models import Station

def parseDatetime(string, default = datetime.datetime.now()):
    return parse_datetime(string) if string else default

# Create your views here.

class DateParser():
    def __init__(self, request):
        self.date       = parse_date(request.GET.get('date', datetime.date.today().isoformat()))
        if not isinstance(self.date, datetime.date):
            self.date  = datetime.date.today()
        self.midnight   = datetime.datetime.combine(self.date, datetime.time()).replace(tzinfo = pytz.UTC)

        self.timeFrom   = self.midnight + datetime.timedelta(days = -0.5)
        self.timeTo     = self.midnight + datetime.timedelta(days = 0.5)

    def context(self):
        return {
            'date':         self.date,
            'currentDate':  (datetime.datetime.now() + datetime.timedelta(days = 0.5)).date(),
            'midnight':     self.midnight,
            'timeFrom':     self.timeFrom,
            'timeTo':       self.timeTo,
        }

@login_required
def listMeteors(request):
    time = DateParser(request)   
    context = {
        'meteors': Meteor.objects.filter(lightmaxTime__gte = time.timeFrom, lightmaxTime__lte = time.timeTo),
    }
    context.update(time.context())
    return render(request, 'meteors/list-meteors.html', context)

@login_required
def listMeteorsJSON(request):
    meteors = {}
    for meteor in Meteor.objects.all():
        meteors[meteor.id] = meteor.asDict()

    return JsonResponse(meteors)

@login_required
def listSightings(request):
    time = DateParser(request)   
    context = {
        'sightings': Sighting.objects.filter(lightmaxTime__gte = time.timeFrom, lightmaxTime__lte = time.timeTo),
        'navigation': reverse('listSightings')
    }
    context.update(time.context())
    return render(request, 'meteors/list-sightings.html', context)

@login_required
def listSightingsStation(request, stationCode):
    time = DateParser(request)   
    context = {
        'station': Station.objects.get(code = stationCode),
        'sightings': Sighting.objects.filter(lightmaxTime__gte = time.timeFrom, lightmaxTime__lte = time.timeTo, station__code = stationCode),
    }
    context.update(time.context())
    return render(request, 'meteors/list-sightings-station.html', context)
    

@login_required
def meteor(request, id):
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
    print("Meteor created")
    
    stations = Station.objects.all()
    for station in stations:
        station.observe(meteor)
    return HttpResponse(status = 200)

### Currently this is unsafe!

@method_decorator(csrf_exempt, name = 'dispatch')
class MeteorView(View):
    def get(self, request):
        return HttpResponse('result')

    def post(self, request):
        pp(request.POST)
        print(request.FILES)

        try:
            meteor = Meteor.objects.createFromPost(
                timestamp           = request.POST.get('timestamp'),

                beginningLatitude   = request.POST.get('beginningLatitude', None),
                beginningLongitude  = request.POST.get('beginningLongitude', None),
                beginningAltitude   = request.POST.get('beginningAltitude', None),
                beginningTime       = request.POST.get('beginningTime', None),
                
                lightmaxLatitude    = request.POST.get('lightmaxLatitude', None),
                lightmaxLongitude   = request.POST.get('lightmaxLongitude', None),
                lightmaxAltitude    = request.POST.get('lightmaxAltitude', None),
                lightmaxTime        = request.POST.get('lightmaxTime', None),

                endLatitude         = request.POST.get('endLatitude', None),
                endLongitude        = request.POST.get('endLongitude', None),
                endAltitude         = request.POST.get('endAltitude', None),
                endTime             = request.POST.get('endTime', None),

                velocityX           = request.POST.get('velocityX', None),
                velocityY           = request.POST.get('velocityY', None),
                velocityZ           = request.POST.get('velocityZ', None),

                magnitude           = request.POST.get('magnitude', None),
            )
            meteor.save()
            print("Meteor has been saved")

        except Exception as e:
            print(e)
            return HttpResponse(e, status = 400)

        return HttpResponse('Meteor has been accepted', status = 201)
