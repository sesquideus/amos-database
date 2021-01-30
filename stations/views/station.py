import datetime
import http
import pytz
import json
import logging
import django
import numpy as np
import pandas as pd

import core.views
import core.http

from astropy.coordinates import get_sun, AltAz, EarthLocation
from astropy.time import Time

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from matplotlib import pyplot
from matplotlib import ticker, dates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap

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
        station.recent_sightings = Sighting.objects.order_by('-timestamp').for_station(station.code).with_everything()[:10]
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

        sightings = Sighting.objects.for_station(station.code).with_everything().as_scatter(self.start, self.end).values('timestamp', 'magnitude')
        station.df_sightings = pd.DataFrame(list(sightings.values())).fillna(value=np.nan)
        return station


class ScatterView(DataFrameView):
    sunalt = LinearSegmentedColormap('sunalt', {
        'red': [
            (0, 0, 0),
            (0.4, 0, 0),
            (0.5, 0.5, 1),
            (0.6667, 1, 1),
            (1, 1, 1),
        ],
        'green': [
            (0, 0, 0),
            (0.4, 0, 0),
            (0.5, 0.5, 0.2),
            (0.6666, 1, 1),
            (1, 1, 1),
        ],
        'blue': [
            (0, 0, 0),
            (0.4, 0.3, 0.3),
            (0.5, 1, 0.2),
            (0.6667, 0, 0),
            (1, 1, 0),
        ],
    }, N=1024)

    C_sighting = 'green'

    C_manual = '#F0E000'
    C_automatic = '#7F7F7F'

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

    C_state_daylight = '#F0E000'
    C_state_observing = '#00C000'
    C_state_not_observing = '#404040'
    C_state_manual = '#A000A0'
    C_state_rain_or_humid = '#0000FF'
    C_state_dome_unreachable = '#FF0000'
    C_state_unknown = '#000000'

    C_light_active = '#D0D0E0'
    C_light_not_active = '#000000'
    C_raining = '#0020FF'
    C_not_raining = '#80D080'
    C_no_error = '#C0FFC0'
    C_error = '#FF0000'

    C_device_off = '#202020'
    C_device_on = '#FF8040'

    C_heating_on = '#FF3000'
    C_heating_off = '#A0C0FF'

    C_error_bit = '#FF0000'
    C_no_error_bit = '#000000'
    C_none = '#00000001'

    S_sensor = 160

    def format_sightings(self):
        self.ax_sightings.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:+.1f}"))
        self.ax_sightings.set_ylabel('apparent magnitude')
        self.ax_sightings.invert_yaxis()
        self.ax_sightings.legend(
            handles=[
                Line2D([0], [0], color=self.C_sighting, lw=0, marker='*', label='sighting'),
            ],
            loc=(1.01, 0.82),
        )

    def format_sensors(self):
        legend_mode = self.ax_sensors.legend(
            handles=[
                Line2D([0], [0], color=self.C_manual, lw=4, label='control: manual'),
                Line2D([0], [0], color=self.C_automatic, lw=4, label='control: automatic'),
            ],
            loc=(1.01, 1.09), fontsize='small', labelspacing=0.2,
        )
        legend_state = self.ax_sensors.legend(
            handles=[
                Line2D([0], [0], color=self.C_state_daylight, lw=4, label='state: daylight'),
                Line2D([0], [0], color=self.C_state_observing, lw=4, label='state: observing'),
                Line2D([0], [0], color=self.C_state_not_observing, lw=4, label='state: not observing'),
                Line2D([0], [0], color=self.C_state_manual, lw=4, label='state: manual'),
                Line2D([0], [0], color=self.C_state_rain_or_humid, lw=4, label='state: rain or humidity'),
                Line2D([0], [0], color=self.C_state_dome_unreachable, lw=4, label='state: dome unreachable'),
                Line2D([0], [0], color=self.C_state_unknown, lw=4, label='state: unknown'),
            ],
            loc=(1.01, 0.63), fontsize='small', labelspacing=0.2,
        )
        legend_cover = self.ax_sensors.legend(
            handles=[
                Line2D([0], [0], color=self.C_cover_closed, lw=4, label='cover: closed'),
                Line2D([0], [0], color=self.C_cover_safety, lw=4, label='cover: safety'),
                Line2D([0], [0], color=self.C_cover_closing, lw=4, label='cover: moving'),
                Line2D([0], [0], color=self.C_cover_open, lw=4, label='cover: open'),
                Line2D([0], [0], color=self.C_cover_problem, lw=4, label='cover: problem'),
            ],
            loc=(1.01, 0.29), fontsize='small', labelspacing=0.2,
        )
        self.ax_sensors.legend(
            handles=[
                Line2D([0], [0], color=self.C_light_not_active, lw=4, label='no light'),
                Line2D([0], [0], color=self.C_light_active, lw=4, label='light'),
                Line2D([0], [0], color=self.C_not_raining, lw=4, label='not raining'),
                Line2D([0], [0], color=self.C_raining, lw=4, label='raining'),
                Line2D([0], [0], color=self.C_device_off, lw=4, label='device: off'),
                Line2D([0], [0], color=self.C_device_on, lw=4, label='device: on'),
                Line2D([0], [0], color=self.C_heating_off, lw=4, label='heating: off'),
                Line2D([0], [0], color=self.C_heating_on, lw=4, label='heating: on'),
            ],
            loc=(1.01, -0.23), fontsize='small', labelspacing=0.2,
        )

        self.ax_sensors.add_artist(legend_mode)
        self.ax_sensors.add_artist(legend_state)
        self.ax_sensors.add_artist(legend_cover)

        self.ax_sensors.set_yticks([1, 2, 3.5, 4.5, 5.5, 7, 8, 9, 10.5, 11.5, 12.5, 14])
        self.ax_sensors.set_yticklabels(['lens heating', 'camera heating', 'fan', 'intensifier', 'computer power', \
                'rain closing', 'rain sensor', 'light sensor', 'cover', 'state', 'control', 'Sun'])
        self.ax_sensors.set_ylim(0.5, 14.5)

    def format_temperature(self):
        self.ax_temp.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:.1f} °C"))
        self.ax_temp.set_ylabel('temperature')
        self.ax_temp.legend(
            handles=[
                Line2D([0], [0], color=self.C_T_env, lw=1, label='environment'),
                Line2D([0], [0], color=self.C_T_lens, lw=1, label='lens'),
                Line2D([0], [0], color=self.C_T_CPU, lw=1, label='CPU'),
            ],
            loc=(1.01, 0.29), fontsize='small', labelspacing=0.2,
        )

    def format_humidity(self):
        self.ax_humi.set_ylim(0, 100)
        self.ax_humi.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:.0f} %"))
        self.ax_humi.set_ylabel('Humidity')
        self.ax_humi.legend(
            handles=[
                Line2D([0], [0], color=self.C_H, lw=1, label='relative humidity'),
            ],
            loc=(1.01, 0.41), fontsize='small', labelspacing=0.2,
        )

    def format_storage(self):
        self.ax_storage.set_ylim(ymin=0)
        self.ax_storage.set_ylabel('Storage')
        self.ax_storage.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:.0f} GB"))
        self.ax_storage.legend(
            handles=[
                Line2D([0], [0], color=self.C_primary, lw=1, label='primary'),
                Line2D([0], [0], color=self.C_permanent, lw=1, label='permanent'),
            ],
            loc=(1.01, 0.38), fontsize='small', labelspacing=0.2,
        )

    def render_sightings(self):
        xs = self.object.df_sightings.timestamp.to_numpy()
        ys = self.object.df_sightings.magnitude.to_numpy()
        self.ax_sightings.scatter(xs, ys, s=np.exp(-ys / 2) * 3, color=self.C_sighting, marker='*')

    def render_sensors(self):
        start_floor = self.start.replace(second=0, microsecond=0)
        end_floor = self.end.replace(second=0, microsecond=0)
        full_xs = np.array([start_floor], dtype='datetime64[ns]') + np.arange(0, 1441) * 60 * 1000**3
        frames = AltAz(obstime=full_xs, location=self.object.earth_location())
        alts = get_sun(Time(full_xs)).transform_to(frames).alt


        cov = self.object.df_heartbeat.cover_state.to_numpy()
        cover = np.where(
            cov == 'C', self.C_cover_closed, np.where(
            cov == 'c', self.C_cover_closing, np.where(
            cov == 'S', self.C_cover_safety, np.where(
            cov == 'o', self.C_cover_opening, np.where(
            cov == 'O', self.C_cover_open, self.C_none
        )))))

        sta = self.object.df_heartbeat.state.to_numpy()
        state = np.where(
            sta == Heartbeat.STATE_DAYLIGHT,            self.C_state_daylight, np.where(
            sta == Heartbeat.STATE_OBSERVING,           self.C_state_observing, np.where(
            sta == Heartbeat.STATE_NOT_OBSERVING,       self.C_state_not_observing, np.where(
            sta == Heartbeat.STATE_MANUAL,              self.C_state_manual, np.where(
            sta == Heartbeat.STATE_DOME_UNREACHABLE,    self.C_state_dome_unreachable, np.where(
            sta == Heartbeat.STATE_RAIN_OR_HUMID,       self.C_state_rain_or_humid, self.C_state_unknown
        ))))))

        self.ax_sensors.scatter(full_xs, np.ones(1441) * 14, s=self.S_sensor, c=alts, cmap=self.sunalt, marker='|', vmin=-90, vmax=90)

        self.render_sensor(12.5, self.trivalue(self.object.df_heartbeat.automatic.to_numpy(), self.C_automatic, self.C_manual, self.C_none))
        self.render_sensor(11.5, state)
        self.render_sensor(10.5, cover)

        self.render_sensor( 9.0, self.trivalue(self.object.df_heartbeat.light_sensor_active.to_numpy(), self.C_light_active, self.C_light_not_active, self.C_none))
        self.render_sensor( 8.0, self.trivalue(self.object.df_heartbeat.rain_sensor_active.to_numpy(), self.C_raining, self.C_not_raining, self.C_none))
        self.render_sensor( 7.0, self.trivalue(self.object.df_heartbeat.rain_emergency_closing.to_numpy(), self.C_error_bit, self.C_no_error_bit, self.C_none))

        self.render_sensor( 5.5, self.trivalue(self.object.df_heartbeat.computer_power.to_numpy(), self.C_device_on, self.C_device_off, self.C_none))
        self.render_sensor( 4.5, self.trivalue(self.object.df_heartbeat.intensifier_active.to_numpy(), self.C_device_on, self.C_device_off, self.C_none))
        self.render_sensor( 3.5, self.trivalue(self.object.df_heartbeat.fan_active.to_numpy(), self.C_device_on, self.C_device_off, self.C_none))

        self.render_sensor( 2.0, self.trivalue(self.object.df_heartbeat.camera_heating.to_numpy(), self.C_heating_on, self.C_heating_off, self.C_none))
        self.render_sensor( 1.0, self.trivalue(self.object.df_heartbeat.lens_heating.to_numpy(), self.C_heating_on, self.C_heating_off, self.C_none))

    @staticmethod
    def trivalue(values, colour_on, colour_off, colour_none):
        return np.where(values == None, colour_none, np.where(values, colour_on, colour_off))

    def render_sensor(self, ypos, colour, *args):
        self.ax_sensors.scatter(self.xs, self.ones * ypos, s=self.S_sensor, c=colour, marker='|', *args)

    def render_temperature(self):
        temperature = self.object.df_heartbeat.temperature.to_numpy(na_value=np.nan)
        t_lens = self.object.df_heartbeat.t_lens.to_numpy(na_value=np.nan)
        t_cpu = self.object.df_heartbeat.t_cpu.to_numpy(na_value=np.nan)
        minimum = min([np.nanmin(temperature), np.nanmin(t_lens), np.nanmin(t_cpu)])
        maximum = max([np.nanmax(temperature), np.nanmax(t_lens), np.nanmin(t_cpu)])

        if minimum is np.nan:
            self.ax_temp.set_ylim(0, 20)

        self.ax_temp.scatter(self.xs, temperature, s=0.5, color=self.C_T_env, marker='.')
        self.ax_temp.scatter(self.xs, t_lens, s=0.5, color=self.C_T_lens, marker='.')
        self.ax_temp.scatter(self.xs, t_cpu, s=0.5, color=self.C_T_CPU, marker='.')

    def render_humidity(self):
        self.ax_humi.scatter(self.xs, self.object.df_heartbeat.humidity, s=0.5, color=self.C_H, marker='.')

    def render_storage(self):
        self.ax_storage.scatter(self.xs, self.object.df_heartbeat.storage_permanent_available / 1024**3, s=0.5, color=self.C_permanent, marker='.')
        self.ax_storage.scatter(self.xs, self.object.df_heartbeat.storage_primary_available / 1024**3, s=0.5, color=self.C_primary, marker='.')
        self.ax_storage.set_ylim(ymin=0, ymax=max(
            np.amax(self.object.df_heartbeat.storage_primary_available),
            np.amax(self.object.df_heartbeat.storage_permanent_available)
        ) * 1.05 / 1024**3)

    def render_to_response(self, context, **response_kwargs):
        self.fig, self.axes = pyplot.subplots(5, 1, gridspec_kw={'height_ratios': [2, 4, 2, 2, 2]})
        (self.ax_sightings, self.ax_sensors, self.ax_temp, self.ax_humi, self.ax_storage) = self.axes

        self.fig.set_size_inches(12.8, 10)
        self.fig.tight_layout(rect=(0.07, 0, 0.86, 1))

        for ax in self.axes:
            ax.grid('major', 'both', color='black', linestyle=':', linewidth=0.5, alpha=0.5)
            ax.tick_params(axis='both', which='both', labelsize=10)
            ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
            ax.set_xlim(self.start, self.end)

        self.format_sightings()
        self.format_sensors()
        self.format_temperature()
        self.format_humidity()
        self.format_storage()


        if (len(self.object.df_sightings) > 0):
            self.render_sightings()

        if (len(self.object.df_heartbeat) > 0):
            self.ones = np.ones(len(self.object.df_heartbeat))
            self.xs = self.object.df_heartbeat.timestamp.to_numpy()

            self.render_sensors()
            self.render_temperature()
            self.render_humidity()
            self.render_storage()
        else:
            self.ax_temp.set_ylim(0, 20)
            self.ax_storage.set_ylim(0, 256)

        return core.http.FigurePNGResponse(self.fig)


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
        except Station.DoesNotExist as e:
            return HttpResponse(e, status=http.HTTPStatus.UNPROCESSABLE_ENTITY)
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
