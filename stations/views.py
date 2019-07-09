import datetime
import pytz

from pprint import pprint as pp

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from . import models

# Create your views here.

@login_required
def status(request):
    context = {
        'subnetworks': models.Subnetwork.objects.all(),
    }
    return render(request, 'stations/status.html', context)

def station(request, code):
    station = models.Station.objects.get(code = code)

    context = {
        'station': station,
        'lastDay': station.sighting_set.filter(timestamp__gte = datetime.datetime.now(pytz.utc) - datetime.timedelta(days = 1))
    }
    return render(request, 'stations/station.html', context)

def stationsJSON(request):
    return JsonResponse({station.id: station.asDict() for station in models.Station.objects.all()})

#@method_decorator(login_required, name = 'dispatch')
@method_decorator(csrf_exempt, name = 'dispatch')
class APIView(View):
    def get(self, request):
        return JsonResponse({'ok': 'OK'})
    

    def post(self, request):
        print(f"{'*' * 20} Incoming status report {'*' * 20}")

        pp(request.body)

        return HttpResponse('Status update received', status = 201)
