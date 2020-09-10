import textwrap
import datetime
import pytz
from django.db import models
from django.db.models import F
from django.apps import apps
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator

import core.models


class HeartbeatManager(models.Manager):
    def get_queryset(self):
        return HeartbeatQuerySet(
            model=self.model,
            using=self._db,
            hints=self._hints,
        )

    def create_from_POST(self, code, **kwargs):
        Station = apps.get_model('stations', 'Station')
        heartbeat = self.create(
            timestamp       = kwargs.get('timestamp'),
            station         = Station.objects.get(code=code),
            status          = kwargs.get('status'),
            lid             = kwargs.get('lid'),
            heating         = kwargs.get('heating'),
            temperature     = kwargs.get('temperature'),
            pressure        = kwargs.get('pressure'),
            humidity        = kwargs.get('humidity'),
        )
        return heartbeat


class HeartbeatQuerySet(models.QuerySet):
    def for_station(self, station_code, *, count=10):
        return self.filter(station__code=station_code)[:count]

    def with_age(self):
        return self.annotate(
            age=datetime.datetime.now() - F('timestamp'),
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

    STATE_OBSERVING = 'O'
    STATE_MALFUNCTION = 'M'
    STATE_NOT_OBSERVING = 'N'
    STATES                          = [
                                        (STATE_OBSERVING, 'observing'),
                                        (STATE_MALFUNCTION, 'malfunction'),
                                        (STATE_NOT_OBSERVING, 'not observing'),
                                    ]

    LID_OPEN = 'O'
    LID_CLOSED = 'C'
    LID_PROBLEM = 'P'
    LID_UNKNOWN = 'U'
    LID_STATES                      = [
                                        (LID_OPEN, 'open'),
                                        (LID_CLOSED, 'closed'),
                                        (LID_PROBLEM, 'problem'),
                                        (LID_UNKNOWN, 'unknown'),
                                    ]

    HEATING_OFF = '0'
    HEATING_ON = '1'
    HEATING_PROBLEM = 'P'
    HEATING_STATES                  = [
                                        (HEATING_OFF, 'off'),
                                        (HEATING_ON, 'on'),
                                        (HEATING_PROBLEM, 'problem'),
                                    ]

    objects                         = HeartbeatManager.from_queryset(HeartbeatQuerySet)()

    timestamp                       = models.DateTimeField(
                                        verbose_name        = 'timestamp',
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
    status                          = models.CharField(
                                        max_length          = 1,
                                        choices             = STATES,
                                        null                = True,
                                        blank               = True,
                                    )
    lid                             = models.CharField(
                                        max_length          = 1,
                                        choices             = LID_STATES,
                                        null                = True,
                                        blank               = True,
                                    )
    heating                         = models.CharField(
                                        max_length          = 1,
                                        choices             = HEATING_STATES,
                                        null                = True,
                                        blank               = True,
                                    )
    temperature                     = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                    )
    pressure                        = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                    )
    humidity                        = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                    )

    def __str__(self):
        return f"[{self.timestamp}] {self.station.code} {self.get_status_display()}"

    def get_absolute_url(self):
        return reverse('heartbeat', kwargs = {'code': self.station.code, 'id': self.id})
