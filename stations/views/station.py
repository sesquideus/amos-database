import datetime
import pytz
import json
import logging
import django
import io

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


import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
from matplotlib import ticker, dates
from matplotlib.backends.backend_agg import FigureCanvasAgg


from stations.models import Station, Subnetwork, Heartbeat, LogEntry
from meteors.models import Sighting
from core.views import JSONDetailView, JSONListView, LoginDetailView

log = logging.getLogger(__name__)


class DetailView(LoginDetailView):
    model           = Station
    slug_field      = 'code'
    slug_url_kwarg  = 'code'
    template_name   = 'stations/station/main.html'

    def get_queryset(self, **kwargs):
        return self.model.objects.with_last_heartbeat().with_last_sighting().with_log_entries()

    def get_object(self, **kwargs):
        station = super().get_object(**kwargs)
        station.recent_heartbeats = Heartbeat.objects.order_by('-timestamp').for_station(station.code)[:10]
        station.recent_sightings = Sighting.objects.order_by('-timestamp').for_station(station.code).with_lightmax().with_station()[:10]
#        station.log_entries = LogEntry.objects.for_station(station.code)
        return station


@method_decorator(login_required, name='dispatch')
class DetailViewJSON(JSONDetailView):
    model           = Station
    slug_field      = 'code'
    slug_url_kwarg  = 'code'


@method_decorator(login_required, name='dispatch')
class ListViewJSON(JSONListView):
    model               = Station
    context_object_name = 'stations'


class GraphView(LoginDetailView):
    model           = Station
    slug_field      = 'code'
    slug_url_kwarg  = 'code'
    context_object_name = 'station'

    def format_axes(self, ax):
        return ax

    def get_object(self, **kwargs):
        station = super().get_object(**kwargs)
        station.heartbeats_graph = Heartbeat.objects.for_station(station.code).for_graph()
        station.minutes = [hb['minute'] for hb in station.heartbeats_graph]
        return station

    def render_to_response(self, context, **response_kwargs):
        fig, ax = pyplot.subplots()
        fig.tight_layout(rect=(0.06, 0.08, 1.03, 1))
        fig.set_size_inches(8, 3)
        ax.set_xlim(datetime.datetime.now() - datetime.timedelta(days=1), datetime.datetime.now())
        ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
        ax = self.format_axes(ax)

        canvas = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        pyplot.close(fig)

        response = django.http.HttpResponse(buf.getvalue(), content_type='image/png')
        response['Content-Length'] = str(len(response.content))
        return response


class TemperatureGraphView(GraphView):
    def get_object(self, **kwargs):
        station = super().get_object(**kwargs)
        station.t_env = [hb['temperature'] for hb in station.heartbeats_graph]
        station.t_lens = [hb['t_lens'] for hb in station.heartbeats_graph]
        station.t_cpu = [hb['t_cpu'] for hb in station.heartbeats_graph]
        return station

    def format_axes(self, ax):
        ax.scatter(self.object.minutes, self.object.t_env, marker='.')
        ax.scatter(self.object.minutes, self.object.t_lens, marker='.')
        ax.scatter(self.object.minutes, self.object.t_cpu, marker='.')
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:.0f} °C"))
        return ax


#@method_decorator(login_required, name = 'dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class APIViewHeartbeat(View):
    def get(self, request):
        return django.http.JsonResponse({'ok': 'OK'})

    def post(self, request, code):
        log.info(f"Incoming heartbeat for station {code}")
        pp(request.headers)
        pp(request.body)

        try:
            data = json.loads(request.body)

            report = Heartbeat.objects.create_from_POST(code, **data)
            report.save()

            response = HttpResponse(f"Heartbeat received at {datetime.datetime.utcnow()}", status=201)
        #response['location'] = reverse('station-receive-heartbeat', args=[report.id])
            return response

        except json.JSONDecodeError:
            print("JSON decoding error")
            return HttpResponseBadRequest()
#        except Exception as e:
#            print(e)
#            return HttpResponseBadRequest()


@method_decorator(csrf_exempt, name='dispatch')
class APIViewSighting(View):
    def post(self, request, code):
        log.info(f"Incoming new sighting from station {code}")

        try:
            data = json.loads(request.body)

            sighting = Sighting.objects.create_from_POST(code, **data)

            response = HttpResponse('New sighting received', status=201)
            response['location'] = reverse('sighting', args=[sighting.id])
            return response

        except json.JSONDecodeError:
            log.warning("JSON decoding error in the sighting")
            return HttpResponseBadRequest()
        except Exception as e:
            log.warning(e)
            return HttpResponseBadRequest()
