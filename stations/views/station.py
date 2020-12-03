import datetime
import pytz
import json
import logging
import django
import numpy as np
import pandas as pd

import core.views
import core.http

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from matplotlib import pyplot
from matplotlib import ticker, dates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from stations.models import Station, Subnetwork, Heartbeat, LogEntry
from meteors.models import Sighting

log = logging.getLogger(__name__)


def floor_to(time, interval):
    return datetime.datetime.fromtimestamp(time.timestamp() // interval * interval).replace(tzinfo=pytz.utc)


class DetailView(core.views.LoginDetailView):
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
class DetailViewJSON(core.views.JSONDetailView):
    model           = Station
    slug_field      = 'code'
    slug_url_kwarg  = 'code'


@method_decorator(login_required, name='dispatch')
class ListViewJSON(core.views.JSONListView):
    model               = Station
    context_object_name = 'stations'


class DataFrameView(core.views.LoginDetailView):
    model = Station
    slug_field = 'code'
    slug_url_kwarg = 'code'
    context_object_name = 'station'

    def get_object(self, **kwargs):
        station = super().get_object(**kwargs)

        self.start = kwargs.get('start', datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(days=1))
        self.end = kwargs.get('end', datetime.datetime.now(tz=pytz.utc))

        heartbeats = Heartbeat.objects.for_station(station.code).as_scatter(self.start, self.end)
        station.df_heartbeat = pd.DataFrame(list(heartbeats.values()))

        sightings = Sighting.objects.for_station(station.code).as_scatter(self.start, self.end)
        station.df_sightings = pd.DataFrame(list(sightings.values()))
        return station


class GraphView(DataFrameView):
    def render_to_response(self, context, **response_kwargs):
        fig, ax = pyplot.subplots()
        fig.tight_layout(rect=(0.05, 0.05, 1.03, 1))
        fig.set_size_inches(12, 3)
        ax.set_xlim(self.start, self.end)
        ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
        ax.grid('major', 'both', color='black', linestyle=':', linewidth=0.5, alpha=0.5)

        if len(self.object.df_heartbeat) == 0:
            pass
        else:
            fig, ax = self.format_axes(fig, ax)

        return core.http.FigurePNGResponse(fig)


class ScatterView(DataFrameView):
    def render_to_response(self, context, **response_kwargs):
        C_sighting = 'green'

        C_T_env = '#00D040'
        C_T_lens = '#0030B0'
        C_T_CPU = '#E01040'
        C_H = '#0080C0'
        C_primary = '#FF8000'
        C_permanent = '#00A040'

        C_cover_closed = '#400060'
        C_cover_open = '#FFC000'
        C_cover_opening = '#A08060'
        C_cover_closing = '#A08060'
        C_cover_safety = '#008080'
        C_cover_problem = '#FF0000'

        C_light_active = '#D0D0E0'
        C_light_not_active = '#000000'
        C_raining = '#0020FF'
        C_not_raining = '#80D080'

        C_device_off = '#202020'
        C_device_on = '#FF8040'

        C_heating_on = '#FF3000'
        C_heating_off = '#A0C0FF'

        fig, (ax_sightings, ax_sensors, ax_temp, ax_humi, ax_storage) = pyplot.subplots(5, 1, sharex=True)
        fig.set_size_inches(12.8, 8)
        fig.tight_layout(rect=(0.07, 0, 0.87, 1))

        for ax in [ax_sightings, ax_temp, ax_humi, ax_storage, ax_sensors]:
            ax.grid('major', 'both', color='black', linestyle=':', linewidth=0.5, alpha=0.5)

        ax_sightings.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:+.1f}"))
        ax_sightings.set_ylabel('apparent magnitude')
        ax_sightings.invert_yaxis()
        ax_sightings.legend(
            handles=[
                Line2D([0], [0], color=C_sighting, lw=0, marker='*', label='sighting'),
            ],
            loc=(1.01, 0.8),
        )

        ax_temp.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:.1f} °C"))
        ax_temp.set_ylabel('temperature')
        ax_temp.legend(
            handles=[
                Line2D([0], [0], color=C_T_env, lw=1, label='environment'),
                Line2D([0], [0], color=C_T_lens, lw=1, label='lens'),
                Line2D([0], [0], color=C_T_CPU, lw=1, label='CPU'),
            ],
            loc=(1.01, 0.0),
        )

        ax_humi.set_ylim(0, 100)
        ax_humi.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:.0f} %"))
        ax_humi.set_ylabel('Humidity')
        ax_humi.legend(['relative humidity'])

        ax_humi.legend(
            handles=[
                Line2D([0], [0], color=C_H, lw=1, label='relative humidity'),
            ],
            loc=(1.01, 0.4),
        )

        ax_storage.set_ylim(0, 256)
        ax_storage.set_ylabel('Storage')
        ax_storage.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:.0f} GB"))
        ax_storage.legend(['primary', 'permanent'])

        ax_storage.legend(
            handles=[
                Line2D([0], [0], color=C_primary, lw=1, label='primary'),
                Line2D([0], [0], color=C_permanent, lw=1, label='permanent'),
            ],
            loc=(1.01, 0.3),
        )

        ax_sensors.set_xlim(self.start, self.end)
        ax_sensors.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
        ax_sensors.set_yticks([1, 2, 4, 5, 6, 8, 9, 11])
        ax_sensors.set_yticklabels(['lens heating', 'camera heating', 'fan', 'intensifier', 'computer power', 'rain sensor', 'light sensor', 'cover'])
        ax_sensors.set_ylim(0.5, 11.5)

        ax_sensors.legend(
            handles=[
                Line2D([0], [0], color=C_cover_closed, lw=4, label='cover: closed'),
                Line2D([0], [0], color=C_cover_safety, lw=4, label='cover: safety'),
                Line2D([0], [0], color=C_cover_open, lw=4, label='cover: open'),
                Line2D([0], [0], color=C_cover_problem, lw=4, label='cover: problem'),
                Line2D([0], [0], color=C_light_not_active, lw=4, label='no light'),
                Line2D([0], [0], color=C_light_active, lw=4, label='light'),
                Line2D([0], [0], color=C_not_raining, lw=4, label='not raining'),
                Line2D([0], [0], color=C_raining, lw=4, label='raining'),
                Line2D([0], [0], color=C_device_off, lw=4, label='device: off'),
                Line2D([0], [0], color=C_device_on, lw=4, label='device: on'),
                Line2D([0], [0], color=C_heating_off, lw=4, label='heating: off'),
                Line2D([0], [0], color=C_heating_on, lw=4, label='heating: on'),
            ],
            ncol=1,
            loc=(1.01, -0.5),
        )

        if (len(self.object.df_heartbeat) == 0):
            return core.http.FigurePNGResponse(fig)

        xs = self.object.df_sightings.timestamp.to_numpy()
        ax_sightings.scatter(xs, self.object.df_sightings.magnitude, s=np.exp(-self.object.df_sightings.magnitude / 2) * 3, color=C_sighting, marker='*')

        xs = self.object.df_heartbeat.timestamp.to_numpy()

        ax_temp.scatter(xs, self.object.df_heartbeat.temperature, s=0.5, color=C_T_env, marker='.')
        ax_temp.scatter(xs, self.object.df_heartbeat.t_lens, s=0.5, color=C_T_lens, marker='.')
        ax_temp.scatter(xs, self.object.df_heartbeat.t_cpu, s=0.5, color=C_T_CPU, marker='.')

        ax_humi.scatter(xs, self.object.df_heartbeat.humidity, s=0.5, color=C_H, marker='.')

        ax_storage.scatter(xs, self.object.df_heartbeat.storage_primary_available, color=C_primary, marker='*')
        ax_storage.scatter(xs, self.object.df_heartbeat.storage_permanent_available, color=C_permanent, marker='*')

        ones = np.ones(len(self.object.df_heartbeat))

        cov = self.object.df_heartbeat.cover_state.to_numpy()
        cover = np.where(
            cov == 'C', C_cover_closed, np.where(
            cov == 'c', C_cover_closing, np.where(
            cov == 'S', C_cover_safety, np.where(
            cov == 'o', C_cover_opening, np.where(
            cov == 'O', C_cover_open, C_cover_problem,
        )))))
        ax_sensors.scatter(xs, ones * 11, s=150, c=cover, marker='|', vmin=0, vmax=5)

        ax_sensors.scatter(xs, ones * 9, s=150, c=np.where(self.object.df_heartbeat.light_sensor_active.to_numpy(), C_light_active, C_light_not_active), marker='|', vmin=0, vmax=1)
        ax_sensors.scatter(xs, ones * 8, s=150, c=np.where(self.object.df_heartbeat.rain_sensor_active.to_numpy(), C_raining, C_not_raining), marker='|', vmin=0, vmax=1)

        ax_sensors.scatter(xs, ones * 6, s=150, c=np.where(self.object.df_heartbeat.computer_power.to_numpy(), C_device_on, C_device_off), marker='|', vmin=0, vmax=1)
        ax_sensors.scatter(xs, ones * 5, s=150, c=np.where(self.object.df_heartbeat.intensifier_active.to_numpy(), C_device_on, C_device_off), marker='|', vmin=0, vmax=1)
        ax_sensors.scatter(xs, ones * 4, s=150, c=np.where(self.object.df_heartbeat.fan_active.to_numpy(), C_device_on, C_device_off), marker='|', vmin=0, vmax=1)

        ax_sensors.scatter(xs, ones * 2, s=150, c=np.where(self.object.df_heartbeat.camera_heating.to_numpy(), C_heating_on, C_heating_off), marker='|', vmin=0, vmax=1)
        ax_sensors.scatter(xs, ones * 1, s=150, c=np.where(self.object.df_heartbeat.lens_heating.to_numpy(), C_heating_on, C_heating_off), marker='|', vmin=0, vmax=1)

        ax_sensors.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))

        return core.http.FigurePNGResponse(fig)


class TemperatureScatterView(GraphView):
    def format_axes(self, fig, ax):
        ax.scatter(self.object.df_heartbeat.timestamp, self.object.df_heartbeat.temperature, s=0.5, color=(0, 0.8, 0.3), marker='.')
        ax.scatter(self.object.df_heartbeat.timestamp, self.object.df_heartbeat.t_lens, s=0.5, color=(0, 0.2, 0.7), marker='.')
        ax.scatter(self.object.df_heartbeat.timestamp, self.object.df_heartbeat.t_cpu, s=0.5, color=(1, 0, 0.2), marker='.')
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:.1f} °C"))
        return fig, ax


class HumidityScatterView(GraphView):
    def format_axes(self, fig, ax):
        ax.scatter(self.object.df_heartbeat.timestamp, self.object.df_heartbeat.humidity, s=0.5, color=(0, 0.6, 1), marker='.')
        ax.set_ylim(0, 100)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:.0f} %"))
        return fig, ax


class SensorsScatterView(GraphView):
    def format_axes(self, fig, ax):
        ones = np.ones(len(self.object.df_heartbeat))
        xs = self.object.df_heartbeat.timestamp.to_numpy()

        def normalize(what, min, max):
            return what.astype(float).to_numpy() * (max - min) + min

        cover = self.object.df_heartbeat.cover_state.replace('C', 0).replace('c', 1).replace('S', 2).replace('o', 3).replace('O', 4).replace('P', 5)
        ax.scatter(xs, ones * 11, s=100, c=cover.to_numpy(), cmap='viridis_r', marker='|', vmin=0, vmax=5)

        ax.scatter(xs, ones * 9, s=100, c=normalize(self.object.df_heartbeat.light_sensor_active, 0.2, 0.5), cmap='plasma', marker='|', vmin=0, vmax=1)
        ax.scatter(xs, ones * 8, s=100, c=self.object.df_heartbeat.rain_sensor_active.to_numpy(), cmap='winter_r', marker='|', vmin=0, vmax=1)

        ax.scatter(xs, ones * 6, s=100, c=self.object.df_heartbeat.computer_power.to_numpy(), cmap='copper', marker='|', vmin=0, vmax=1)
        ax.scatter(xs, ones * 5, s=100, c=self.object.df_heartbeat.intensifier_active.to_numpy(), cmap='copper', marker='|', vmin=0, vmax=1)
        ax.scatter(xs, ones * 4, s=100, c=self.object.df_heartbeat.fan_active.to_numpy(), cmap='copper', marker='|', vmin=0, vmax=1)

        ax.scatter(xs, ones * 2, s=100, c=normalize(self.object.df_heartbeat.camera_heating, 0, 1), cmap='bwr', marker='|', vmin=0, vmax=1)
        ax.scatter(xs, ones * 1, s=100, c=normalize(self.object.df_heartbeat.lens_heating, 0, 1), cmap='bwr', marker='|', vmin=0, vmax=1)

        ax.set_yticks([1, 2, 4, 5, 6, 8, 9, 11])
        ax.set_yticklabels(['lens heating', 'camera heating', 'fan', 'intensifier', 'computer power', 'rain sensor', 'light sensor', 'cover'])
        ax.set_ylim(0.5, 11.5)
        fig.set_size_inches(12, 2)
        return fig, ax


class TemperaturePandasGraphView(GraphView):
    def format_axes(self, ax):
        print(self.object.df_heartbeat)
        ax.plot(self.object.df_heartbeat.index, self.object.df_heartbeat.t_env, linewidth=0.5, color=(0, 0.8, 0.3), marker='.')
        ax.scatter(self.object.df_heartbeat.index, self.object.df_heartbeat.t_len, s=0.5, color=(0, 0.2, 0.7), marker='.')
        ax.scatter(self.object.df_heartbeat.index, self.object.df_heartbeat.t_CPU, s=0.5, color=(1, 0, 0.2), marker='.')
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:.1f} °C"))
        return ax

class HumidityGraphView(GraphView):
    def format_axes(self, ax):
        ax.scatter(self.object.df_heartbeat.index, self.object.df_heartbeat.h_env, s=0.5, color=(0, 0.6, 1), marker='.')
        ax.set_ylim(0, 100)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:.0f} %"))
        return ax

class SensorsGraphView(GraphView):
    def get_q(self):
        return Heartbeat.objects.for_station(self.station.code).as_sensors_graph(self.start, self.end, self.interval)

    def format_axes(self, ax):
        print(self.object.df_heartbeat.to_numpy().transpose())
        ax.imshow(self.object.df_heartbeat.values)
        return ax


class GraphViewJSON(core.views.JsonResponseMixin, DataFrameView):
    def get_context_data(self, **kwargs):
        return self.object.df_heartbeat.to_dict(orient='index')


class DataFrameAggView(core.views.LoginDetailView):
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

        self.station.df_heartbeat = timestamps.merge(data, how="left", on="time")
        self.station.df_heartbeat.set_index('time', inplace=True)
        return self.station


@method_decorator(csrf_exempt, name='dispatch')
class APIViewHeartbeat(django.views.View):
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
            response['location'] = reverse('station-receive-heartbeat', args=[report.id])
            return response

        except json.JSONDecodeError:
            print("JSON decoding error")
            return HttpResponseBadRequest()
#        except Exception as e:
#            print(e)
#            return HttpResponseBadRequest()


@method_decorator(csrf_exempt, name='dispatch')
class APIViewSighting(django.views.View):
    def post(self, request, code):
        log.info(f"Incoming new sighting from station {code}")

        try:
#            pp(request.content_type)
#            pp(request.POST)
#            pp(request.FILES)

            data = {
                'meta': json.loads(request.POST['meta']),
                'files': request.FILES,
            }

            sighting = Sighting.objects.create_from_POST(code, **data)

            response = HttpResponse(f"New sighting received (id {sighting.id})", status=201)
            response['location'] = reverse('sighting', args=[sighting.id])
            return response

        except json.JSONDecodeError:
            log.warning("JSON decoding error in the sighting")
            return HttpResponseBadRequest()

    def get(self, request, code):
        return HttpResponse('Nothing to see here', status=201)
