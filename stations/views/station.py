import datetime
import pytz
import json
import logging
import django
import io
import numpy as np
import pandas as pd

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
from core.views import JSONDetailView, JSONListView, LoginDetailView, JsonResponseMixin

log = logging.getLogger(__name__)


def floor_to(time, interval):
    return datetime.datetime.fromtimestamp(time.timestamp() // interval * interval).replace(tzinfo=pytz.utc)


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


class DataFrameView(LoginDetailView):
    model = Station
    slug_field = 'code'
    slug_url_kwarg = 'code'
    context_object_name = 'station'

    def get_object(self, **kwargs):
        station = super().get_object(**kwargs)

        self.start = kwargs.get('start', datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(days=1))
        self.end = kwargs.get('end', datetime.datetime.now(tz=pytz.utc))

        data = Heartbeat.objects.for_station(station.code).as_scatter(self.start, self.end)
        station.df = pd.DataFrame(list(data.values()))
        return station


class GraphView(DataFrameView):
    def render_to_response(self, context, **response_kwargs):
        fig, ax = pyplot.subplots()
        fig.tight_layout(rect=(0.05, 0.05, 1.03, 1))
        fig.set_size_inches(8, 3)
        ax.set_xlim(self.start, self.end)
        ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
        ax.grid('major', 'both', color='black', linestyle=':', linewidth=0.5, alpha=0.5)
        fig, ax = self.format_axes(fig, ax)

        canvas = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        pyplot.close(fig)

        response = django.http.HttpResponse(buf.getvalue(), content_type='image/png')
        response['Content-Length'] = str(len(response.content))
        return response


class TemperatureScatterView(GraphView):
    def format_axes(self, fig, ax):
        ax.scatter(self.object.df.timestamp, self.object.df.temperature, s=0.5, color=(0, 0.8, 0.3), marker='.')
        ax.scatter(self.object.df.timestamp, self.object.df.t_lens, s=0.5, color=(0, 0.2, 0.7), marker='.')
        ax.scatter(self.object.df.timestamp, self.object.df.t_cpu, s=0.5, color=(1, 0, 0.2), marker='.')
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:.1f} °C"))
        return fig, ax

class HumidityScatterView(GraphView):
    def format_axes(self, fig, ax):
        ax.scatter(self.object.df.timestamp, self.object.df.humidity, s=0.5, color=(0, 0.6, 1), marker='.')
        ax.set_ylim(0, 100)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:.0f} %"))
        return fig, ax

class SensorsScatterView(GraphView):
    def format_axes(self, fig, ax):
        ones = np.ones(len(self.object.df))
        xs = self.object.df.timestamp.to_numpy()

        cover = self.object.df.cover_state.replace('C', 0).replace('c', 1).replace('o', 3).replace('O', 4)

        ax.scatter(xs, ones * 1, s=100, c=self.object.df.lens_heating.to_numpy(), cmap='bwr_r', marker='|')
        ax.scatter(xs, ones * 2, s=100, c=self.object.df.camera_heating.to_numpy(), cmap='bwr_r', marker='|')
        ax.scatter(xs, ones * 3, s=100, c=self.object.df.fan_active.to_numpy(), cmap='bwr_r', marker='|')
        ax.scatter(xs, ones * 4, s=100, c=self.object.df.intensifier_active.to_numpy(), cmap='bwr_r', marker='|')
        ax.scatter(xs, ones * 6, s=100, c=self.object.df.rain_sensor_active.to_numpy(), cmap='bwr_r', marker='|')
        ax.scatter(xs, ones * 7, s=100, c=self.object.df.light_sensor_active.to_numpy(), cmap='bwr_r', marker='|')
        ax.scatter(xs, ones * 8, s=100, c=self.object.df.computer_power.to_numpy(), cmap='bwr_r', marker='|')
        ax.scatter(xs, ones * 10, s=100, c=cover.to_numpy(), cmap='viridis', marker='|')
        ax.set_yticks([1, 2, 3, 4, 6, 7, 8, 10])
        ax.set_yticklabels(['lens', 'camera', 'fan', 'intensifier', 'rain', 'light', 'computer', 'cover'])
        ax.set_ylim(0.5, 10.5)
        fig.set_size_inches(8, 2)
        return fig, ax


class TemperaturePandasGraphView(GraphView):
    def format_axes(self, ax):
        print(self.object.df)
        ax.plot(self.object.df.index, self.object.df.t_env, linewidth=0.5, color=(0, 0.8, 0.3), marker='.')
        ax.scatter(self.object.df.index, self.object.df.t_len, s=0.5, color=(0, 0.2, 0.7), marker='.')
        ax.scatter(self.object.df.index, self.object.df.t_CPU, s=0.5, color=(1, 0, 0.2), marker='.')
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:.1f} °C"))
        return ax

class HumidityGraphView(GraphView):
    def format_axes(self, ax):
        ax.scatter(self.object.df.index, self.object.df.h_env, s=0.5, color=(0, 0.6, 1), marker='.')
        ax.set_ylim(0, 100)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:.0f} %"))
        return ax

class SensorsGraphView(GraphView):
    def get_q(self):
        return Heartbeat.objects.for_station(self.station.code).as_sensors_graph(self.start, self.end, self.interval)

    def format_axes(self, ax):
        print(self.object.df.to_numpy().transpose())
        ax.imshow(self.object.df.values)
        return ax


class GraphViewJSON(JsonResponseMixin, DataFrameView):
    def get_context_data(self, **kwargs):
        return self.object.df.to_dict(orient='index')


class DataFrameAggView(LoginDetailView):
    model = Station
    slug_field = 'code'
    slug_url_kwarg = 'code'
    context_object_name = 'station'

    def get_q(self):
        return Heartbeat.objects.for_station(self.station.code).as_graph(self.start, self.end, self.interval)

    def get_object(self, **kwargs):
        self.station = super().get_object(**kwargs)

        self.interval = kwargs.get('interval', 600)
        self.start = kwargs.get('start', datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(days=1))
        self.end = kwargs.get('end', datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(seconds=self.interval))

        self.start = floor_to(self.start, self.interval)
        self.end = floor_to(self.end, self.interval)

        timestamps = np.arange(self.start, self.end, datetime.timedelta(seconds=self.interval))
        data = self.get_q()

        timestamps = pd.DataFrame(data=timestamps, columns=['time'], dtype='datetime64[ns, UTC]')
        if data:
            data = pd.DataFrame.from_records(data, index='time')
        else:
            data = pd.DataFrame(columns=['time', 't_env', 't_CPU', 't_len', 'h_env'])
            data.set_index('time', inplace=True)

        self.station.df = timestamps.merge(data, how="left", on="time")
        self.station.df.set_index('time', inplace=True)
        return self.station




#@method_decorator(login_required, name = 'dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class APIViewHeartbeat(View):
    def get(self, request):
        return django.http.JsonResponse({'ok': 'OK'})

    def post(self, request, code):
        log.info(f"Incoming heartbeat for station {code}")
#        pp(request.headers)
#        pp(request.body)

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
