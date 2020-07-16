import datetime
import random
import numpy as np
from pprint import pprint as pp

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from core.utils import DateParser
from core.views import JSONDetailView, JSONListView

from meteors.models import Meteor, Sighting
from meteors.forms import DateForm

from stations.models import Station, Subnetwork


@method_decorator(login_required, name = 'dispatch')
class ListDateView(ListView):
    model               = Meteor
    context_object_name = 'meteors'
    template_name       = 'meteors/list-meteors.html'

    def get_queryset(self):
        if self.request.GET.get('date'):
            self.date = datetime.datetime.strptime(self.request.GET['date'], '%Y-%m-%d').date()
        else:
            self.date = datetime.date.today()
        return Meteor.objects.with_sightings().for_night(self.date)

    def get_context_data(self):
        context = super().get_context_data()
        context.update({
            'date':         self.date,
            'form':         DateForm(initial={'date': self.date}),
            'navigation':   reverse('list-meteors')
        })
#        context.update(self.time.context())
        return context

    def post(self, request):
        form = DateForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(f"{reverse('list-meteors')}?date={form.cleaned_data['date'].strftime('%Y-%m-%d')}")
        else:
            return HttpResponseBadRequest()


@login_required
def singleKML(request, name):
    context = {
        'meteor': Meteor.objects.get(name = name)
    }
    return render(request, 'meteors/meteor.kml', context, content_type='application/vnd.google-earth.kml+xml')


@login_required
def singleJSON(request, name):
    meteor = Meteor.objects.get(name = name)
    data = serializers.serialize('json', [meteor])
    return JsonResponse(data, safe = False)


@method_decorator(login_required, name = 'dispatch')
class SingleViewJSON(JSONDetailView):
    model           = Meteor
    slug_field      = 'name'
    slug_url_kwarg  = 'name'


@login_required
def listJSON(request):
    meteors = {}
    for meteor in Meteor.objects.all():
        meteors[meteor.id] = meteor.as_dict()

    return JsonResponse(meteors)


@method_decorator(login_required, name = 'dispatch')
class SingleView(DetailView):
    model           = Meteor
    slug_field      = 'name'
    slug_url_kwarg  = 'name'
    template_name   = 'meteors/meteor.html'

    def get_object(self):
        return Meteor.objects.with_sightings().with_neighbours().get(name=self.kwargs.get('name'))


@method_decorator(csrf_exempt, name = 'dispatch')
class APIView(View):
    def get(self, request):
        return HttpResponse('result')

    def post(self, request):
        print(f"{'*' * 20} Incoming meteor {'*' * 20}")
        #pp(request.POST)
        #pp(request.FILES)

        meteor = Meteor.objects.createFromPost(
            timestamp           = datetime.datetime.strptime(request.POST.get('timestamp', None), '%Y-%m-%d %H:%M:%S.%f%z'),

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
        stations = list(filter(lambda x: np.random.uniform(0, 1) > 0.2, stationsList))

        for station in stations:
            Sighting.objects.createForMeteor(meteor, station)

        print("Meteor has been saved")

        response = HttpResponse('Meteor has been accepted', status = 201)
        response['location'] = reverse('meteor', args = [meteor.name])
        return response
