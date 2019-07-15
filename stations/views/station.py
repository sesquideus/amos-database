import datetime
import pytz
import json

from pprint import pprint as pp

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from django.views.generic.detail import DetailView, BaseDetailView
from django.views.generic.list import ListView

from stations.models import Station, Subnetwork, StatusReport

# Create your views here.

class JSONResponseMixin:
    def render_to_json_response(self, context, **kwargs):
        return JsonResponse(context, **kwargs)

class JSONDetailView(JSONResponseMixin, BaseDetailView):
    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

@login_required
def status(request):
    context = {
        'subnetworks': Subnetwork.objects.all(),
    }
    return render(request, 'stations/status.html', context)

def station(request, code):
    station = Station.objects.get(code = code)

    context = {
        'station': station,
        'lastDay': station.sighting_set.filter(timestamp__gte = datetime.datetime.now(pytz.utc) - datetime.timedelta(days = 1))
    }
    return render(request, 'stations/station.html', context)

def stationsJSON(request):
    return JsonResponse({station.id: station.asDict() for station in Station.objects.all()})


@method_decorator(login_required, name = 'dispatch')
class SingleView(DetailView):
    model           = Station
    slug_field      = 'code'
    slug_url_kwarg  = 'code'
    template_name   = 'stations/station.html'


@method_decorator(login_required, name = 'dispatch')
class JSONView(JSONDetailView):
    model           = Station
    slug_field      = 'code'
    slug_url_kwarg  = 'code'

    
def process(request):
    print(f"{'*' * 20} Incoming status report {'*' * 20}")

    pp(request.body)

    return HttpResponse('Status update received', status = 201)


#@method_decorator(login_required, name = 'dispatch')
@method_decorator(csrf_exempt, name = 'dispatch')
class APIView(View):
    def get(self, request):
        return JsonResponse({'ok': 'OK'})
    
    def post(self, request):
        print(f"{'*' * 20} Incoming status report {'*' * 20}")
        pp(request.body)

        data = json.loads(request.body)

        report = StatusReport.objects.createFromPOST(**data)
        report.save()

        response = HttpResponse('Status update received', status = 201)
        #response['location'] = reverse('statusUpdate', args = [report.id])
        return response
