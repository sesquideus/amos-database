import datetime
import pytz
import json
import logging

from pprint import pprint as pp

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from django.views.generic.detail import DetailView, BaseDetailView
from django.views.generic.list import ListView

from stations.models import Station, Subnetwork, StatusReport
from meteors.models import Sighting
from core.views import JSONDetailView, JSONListView, LoginDetailView

log = logging.getLogger(__name__)


class SingleView(LoginDetailView):
    model           = Station
    slug_field      = 'code'
    slug_url_kwarg  = 'code'
    template_name   = 'stations/station.html'

    def get_object(self, **kwargs):
        station = super().get_object(**kwargs)
        station.recent_reports = StatusReport.objects.order_by('-timestamp').for_station(station.id)[:10]
        station.recent_sightings = Sighting.objects.for_station(station.id).with_lightmax().order_by('-timestamp')[:10]
        return station


@method_decorator(login_required, name = 'dispatch')
class SingleViewJSON(JSONDetailView):
    model           = Station
    slug_field      = 'code'
    slug_url_kwarg  = 'code'


@method_decorator(login_required, name = 'dispatch')
class ListViewJSON(JSONListView):
    model               = Station
    context_object_name = 'stations'


#@method_decorator(login_required, name = 'dispatch')
@method_decorator(csrf_exempt, name = 'dispatch')
class APIView(View):
    def get(self, request):
        return JsonResponse({'ok': 'OK'})

    def post(self, request, code):
        log.info(f"Incoming status report for station {code}")
        #pp(request.headers)
        #pp(request.body)

        try:
            data = json.loads(request.body)

            report = StatusReport.objects.create_from_POST(code, **data)
            report.save()

            response = HttpResponse('Status update received', status = 201)
        #response['location'] = reverse('station-add-status', args = [report.id])
            return response

        except json.JSONDecodeError:
            print("JSON decoding error")
            return HttpResponseBadRequest()
        except Exception as e:
            print(e)
            return HttpResponseBadRequest()


@method_decorator(csrf_exempt, name = 'dispatch')
class APIViewSighting(View):
    def post(self, request, code):
        log.info(f"Incoming new sighting from station {code}")
        #pp(request.headers)
        #pp(request.body)

        try:
            data = json.loads(request.body)

            sighting = Sighting.objects.create_from_POST(code, **data)

            response = HttpResponse('New sighting received', status = 201)
            response['location'] = reverse('sighting', args = [sighting.id])
            return response

        except json.JSONDecodeError:
            log.warning("JSON decoding error in the sighting")
            return HttpResponseBadRequest()
        except Exception as e:
            lor.warning(e)
            return HttpResponseBadRequest()
