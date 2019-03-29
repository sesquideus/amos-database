import datetime
import pytz
import random
import numpy as np
from pprint import pprint as pp

from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime, parse_date
from django.utils.decorators import method_decorator

from astropy.time import Time
from astropy.coordinates import AltAz, get_moon, get_sun

from .models import Meteor, Sighting
from .forms import DateForm
from stations.models import Station, Subnetwork

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


@method_decorator(login_required, name = 'dispatch')
class ListMeteorsView(View):
    def get(self, request):
        time = DateParser(request)   
        context = {
            'meteors': Meteor.objects.filter(lightmaxTime__gte = time.timeFrom, lightmaxTime__lte = time.timeTo),
            'form': DateForm(initial = {'datetime': time.midnight}),
        }
        context.update(time.context())
        return render(request, 'meteors/list-meteors.html', context)

    def post(self, request):
        form = DateForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('listMeteors') + "?date=" + form.cleaned_data['datetime'].strftime("%Y-%m-%d"))
        else:
            return HttpResponseBadRequest()


@login_required
def listMeteorsJSON(request):
    meteors = {}
    for meteor in Meteor.objects.all():
        meteors[meteor.id] = meteor.asDict()

    return JsonResponse(meteors)

@method_decorator(login_required, name = 'dispatch')
class ListSightingsView(View):
    def get(self, request):
        time = DateParser(request)   
        context = {
            'sightings':    Sighting.objects.filter(lightmaxTime__gte = time.timeFrom, lightmaxTime__lte = time.timeTo),
            'form':         DateForm(initial = {'datetime': time.midnight}),
            'navigation':   reverse('listSightings')
        }
        context.update(time.context())
        return render(request, 'meteors/list-sightings.html', context)

    def post(self, request):
        form = DateForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('listSightings') + "?date=" + form.cleaned_data['datetime'].strftime("%Y-%m-%d"))
        else:
            return HttpResponseBadRequest()


@login_required
def listSightingsStation(request, stationCode):
    time = DateParser(request)   
    context = {
        'station': Station.objects.get(code = stationCode),
        'form':         DateForm(initial = {'datetime': time.midnight}),
        'sightings': Sighting.objects.filter(lightmaxTime__gte = time.timeFrom, lightmaxTime__lte = time.timeTo, station__code = stationCode),
    }
    context.update(time.context())
    return render(request, 'meteors/list-sightings-station.html', context)
    


@login_required
def meteorJSON(request, id):
    meteor = Meteor.objects.get(id = id)
    data = serializers.serialize('json', [meteor])
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

@method_decorator(login_required, name = 'dispatch')
class MeteorView(View):
    def get(self, request, id):
        context = {
            'meteor': Meteor.objects.get(id = id),
        } 
        return render(request, 'meteors/meteor.html', context)

@method_decorator(csrf_exempt, name = 'dispatch')
class MeteorAPIView(View):
    def get(self, request):
        return HttpResponse('result')

    def post(self, request):
        print('*' * 20 + "Incoming meteor" + '*' * 20)
        pp(request.POST)
        pp(request.FILES)

        meteor = Meteor.objects.createFromPost(
            timestamp           = request.POST.get('timestamp'),

            beginningLatitude   = request.POST.get('beginningLatitude', None),
            beginningLongitude  = request.POST.get('beginningLongitude', None),
            beginningAltitude   = request.POST.get('beginningAltitude', None),
            beginningTime       = datetime.datetime.strptime(request.POST.get('beginningTime', None), '%Y-%m-%d %H:%M:%S.%f%z'),
            
            lightmaxLatitude    = request.POST.get('lightmaxLatitude', None),
            lightmaxLongitude   = request.POST.get('lightmaxLongitude', None),
            lightmaxAltitude    = request.POST.get('lightmaxAltitude', None),
            lightmaxTime        = datetime.datetime.strptime(request.POST.get('lightmaxTime', None), '%Y-%m-%d %H:%M:%S.%f%z'),

            endLatitude         = request.POST.get('endLatitude', None),
            endLongitude        = request.POST.get('endLongitude', None),
            endAltitude         = request.POST.get('endAltitude', None),
            endTime             = datetime.datetime.strptime(request.POST.get('endTime', None), '%Y-%m-%d %H:%M:%S.%f%z'),

            velocityX           = request.POST.get('velocityX', None),
            velocityY           = request.POST.get('velocityY', None),
            velocityZ           = request.POST.get('velocityZ', None),

            magnitude           = request.POST.get('magnitude', None),
        )
        meteor.save()

        subnetwork = random.choice(Subnetwork.objects.all())
        stationsList = Station.objects.filter(subnetwork__id = subnetwork.id)
        stations = list(filter(lambda x: np.random.uniform(0, 1) > 0.4, stationsList))

        for station in stations:
            Sighting.objects.createForMeteor(meteor, station)       


        print("Meteor has been saved")


        response = HttpResponse('Meteor has been accepted', status = 201)
        response['Location'] = reverse('meteor', args = [meteor.id])
        return response
