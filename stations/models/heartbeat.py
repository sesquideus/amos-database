import textwrap
import datetime
import pytz
import dotmap

from django.db import models
from django.db.models import F, Func, Aggregate, Prefetch, Avg, Min, Max
from django.db.models.functions import TruncMinute, Extract, Floor
from django.apps import apps
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator

from pprint import pprint as pp

import core.models


class HeartbeatManager(models.Manager):
    def get_queryset(self):
        return HeartbeatQuerySet(
            model=self.model,
            using=self._db,
            hints=self._hints,
        )

    def create_from_POST(self, code, **data):
        Station = apps.get_model('stations', 'Station')

        stateS = data['dome']['s']
        stateT = data['dome']['t']

        #pp(data)
        if stateS is None:
            cover_state = None
        else:
            if stateS[0] != '-':
                if stateS[1] != '-':
                    cover_state = Heartbeat.COVER_OPENING
                else:
                    cover_state = Heartbeat.COVER_CLOSING
            else:
                if stateS[14] != '-':
                    cover_state = Heartbeat.COVER_SAFETY
                else:
                    if stateS[2] != '-':
                        cover_state = Heartbeat.COVER_OPEN
                    elif stateS[3] != '-':
                        cover_state = Heartbeat.COVER_CLOSED
                    else:
                        cover_state = Heartbeat.COVER_PROBLEM

        try:
            station = Station.objects.get(code=code)
        except Station.DoesNotExist as e:
            raise Station.DoesNotExist(f"Station {code} does not exist")

        heartbeat = self.create(
            automatic                   = data['auto'],
            timestamp                   = data['time'],
            station                     = station,

            state                       = data['st'],
            status_string               = stateS,
            lens_heating                = (stateS[4] != '-') if stateS else None,
            camera_heating              = (stateS[5] != '-') if stateS else None,
            intensifier_active          = (stateS[6] != '-') if stateS else None,
            fan_active                  = (stateS[7] != '-') if stateS else None,

            rain_sensor_active          = (stateS[9] != '-') if stateS else None,
            light_sensor_active         = (stateS[10] != '-') if stateS else None,
            computer_power              = (stateS[11] != '-') if stateS else None,

            rain_emergency_closing      = (stateS[25] != '-') if stateS else None,

            temperature                 = None if stateT is None else stateT['t_sht'],
            t_lens                      = None if stateT is None else stateT['t_lens'],
            t_cpu                       = None if stateT is None else stateT['t_cpu'],
            humidity                    = None if stateT is None else stateT['h_sht'],

            cover_state                 = cover_state,
            cover_position              = None if data['dome']['z'] is None else data['dome']['z']['sp'],

            storage_primary_available   = data['disk']['prim']['a'],
            storage_primary_total       = data['disk']['prim']['t'],
            storage_permanent_available = data['disk']['perm']['a'],
            storage_permanent_total     = data['disk']['perm']['t'],
        )
        return heartbeat


class HeartbeatQuerySet(models.QuerySet):
    def for_station(self, station_code):
        return self.filter(station__code=station_code)

    def with_age(self):
        return self.annotate(
            age=datetime.datetime.now() - F('timestamp'),
        )

    def with_station(self):
        Station = apps.get_model('stations', 'Station')
        return self.prefetch_related(
            Prefetch(
                'station',
                queryset=Station.objects.with_subnetwork(),
            )
        )

    def for_floored_interval(self, start=None, end=None, interval=60):
        if end == None:
            end = datetime.datetime.now(tz=pytz.utc)
        if start == None:
            start = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(days=1)

        return self.filter(
                timestamp__range=(start, end)
            ).order_by(
                'timestamp'
            ).annotate(
                unix=Floor(Extract('timestamp', 'epoch') / interval) * interval,
                time=Func(F('unix'), function="TO_TIMESTAMP", output_field=models.DateTimeField()),
            )

    def as_graph(self, start=None, end=None, interval=60):
        return self.for_floored_interval(
                start, end, interval
            ).values(
                'time',
            ).annotate(
                t_env=Avg('temperature'),
                h_env=Avg('humidity'),
                t_len=Avg('t_lens'),
                t_CPU=Avg('t_cpu'),
                cover=Max('cover_state'),
            ).order_by()

    def as_sensors_graph(self, start=None, end=None, interval=60):
        return self.for_floored_interval(
                start, end, interval
            ).values(
                'time',
            ).annotate(
                t_env=Avg('temperature'),
                lh=BoolOr('lens_heating'),
                ch=BoolOr('camera_heating'),
                ii=BoolOr('intensifier_active'),
                fa=BoolOr('fan_active'),
                rs=BoolOr('rain_sensor_active'),
                ls=BoolOr('light_sensor_active'),
                cp=BoolOr('computer_power')
            ).order_by()

    def as_scatter(self, start=None, end=None):
        if end == None:
            end = datetime.datetime.now(tz=pytz.utc)
        if start == None:
            start = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(days=1)

        return self.filter(
            timestamp__range=(start, end)
        ).order_by(
            'timestamp'
        )


class Heartbeat(models.Model):
    class Meta:
        verbose_name                = 'heartbeat report'
        verbose_name_plural         = 'heartbeat reports'
        ordering                    = ['-timestamp']
        get_latest_by               = ['timestamp']
        indexes                     = [
                                        models.Index(fields=['timestamp', 'station']),
                                    ]

    STATE_DAYLIGHT = 'D'
    STATE_OBSERVING = 'O'
    STATE_NOT_OBSERVING = 'N'
    STATE_MANUAL = 'M'
    STATE_DOME_UNREACHABLE = 'U'
    STATE_RAIN_OR_HUMID = 'R'
    STATE_UNKNOWN = '?'
    STATES                          = [
                                        (STATE_OBSERVING, 'observing'),
                                        (STATE_NOT_OBSERVING, 'not observing'),
                                        (STATE_DAYLIGHT, 'day'),
                                        (STATE_MANUAL, 'manual'),
                                        (STATE_DOME_UNREACHABLE, 'dome unreachable'),
                                        (STATE_RAIN_OR_HUMID, 'rain or humidity'),
                                        (STATE_UNKNOWN, 'unknown'),
                                    ]

    COVER_OPEN = 'O'
    COVER_OPENING = 'o'
    COVER_CLOSED = 'C'
    COVER_CLOSING = 'c'
    COVER_PROBLEM = 'P'
    COVER_SAFETY = 'S'
    COVER_STATES                    = [
                                        (COVER_OPEN, 'open'),
                                        (COVER_OPENING, 'opening'),
                                        (COVER_CLOSED, 'closed'),
                                        (COVER_CLOSING, 'closing'),
                                        (COVER_PROBLEM, 'problem'),
                                        (COVER_SAFETY, 'safety'),
                                    ]

    objects                         = HeartbeatManager.from_queryset(HeartbeatQuerySet)()

    timestamp                       = models.DateTimeField(
                                        verbose_name        = 'timestamp',
                                        blank               = True,
                                        auto_now_add        = True,
                                    )
    received                        = models.DateTimeField(
                                        verbose_name        = 'received at',
                                        auto_now_add        = True,
                                    )

    station                         = models.ForeignKey(
                                        'Station',
                                        on_delete           = models.CASCADE,
                                        related_name        = 'heartbeats',
                                    )
    state                           = models.CharField(
                                        max_length          = 1,
                                        choices             = STATES,
                                        null                = True,
                                        blank               = True,
                                    )
    cover_state                     = models.CharField(
                                        max_length          = 1,
                                        choices             = COVER_STATES,
                                        null                = True,
                                        blank               = True,
                                    )

    # Device sensors
    status_string                   = models.CharField(null=True, blank=True, max_length=32)
    lens_heating                    = models.BooleanField(null=True, blank=True)
    camera_heating                  = models.BooleanField(null=True, blank=True)
    intensifier_active              = models.BooleanField(null=True, blank=True)
    fan_active                      = models.BooleanField(null=True, blank=True)
    rain_sensor_active              = models.BooleanField(null=True, blank=True)
    light_sensor_active             = models.BooleanField(null=True, blank=True)
    computer_power                  = models.BooleanField(null=True, blank=True)
    rain_emergency_closing          = models.BooleanField(null=True, blank=True)
    cover_position                  = models.SmallIntegerField(null=True, blank=True)

    # Environmental data
    temperature                     = models.FloatField(null=True, blank=True)
    t_lens                          = models.FloatField(null=True, blank=True)
    t_cpu                           = models.FloatField(null=True, blank=True)
    humidity                        = models.FloatField(null=True, blank=True)

    # Storage
    storage_primary_available       = models.BigIntegerField(null=True, blank=True)
    storage_primary_total           = models.BigIntegerField(null=True, blank=True)
    storage_permanent_available     = models.BigIntegerField(null=True, blank=True)
    storage_permanent_total         = models.BigIntegerField(null=True, blank=True)

    # Management
    automatic                       = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return f"[{self.station.code}] at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')}: {self.status_string}"

    def get_absolute_url(self):
        return reverse('heartbeat', kwargs={'code': self.station.code, 'id': self.id})
