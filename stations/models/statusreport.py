import textwrap
import datetime
import pytz
from django.db import models
from django.apps import apps
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator

import core.models


class StatusReportManager(models.Manager):
    def get_queryset(self):
        return StatusReportQuerySet(
            model=self.model,
            using=self._db,
            hints=self._hints,
        )

    def create_from_POST(self, code, **kwargs):
        Station = apps.get_model('stations', 'Station')
        report = self.create(
            timestamp       = kwargs.get('timestamp'),
            station         = Station.objects.get(code=code),
            status          = kwargs.get('status'),
            lid             = kwargs.get('lid'),
            heating         = kwargs.get('heating'),
            temperature     = kwargs.get('temperature'),
            pressure        = kwargs.get('pressure'),
            humidity        = kwargs.get('humidity'),
        )
        return report


class StatusReportQuerySet(models.QuerySet):
    def for_station(self, station_id, *, count=10):
        return self.filter(station__id=station_id)[:count]

    def with_age(self):
        return self.annotate(
            age=datetime.datetime.now() - F('timestamp'),
        )


class StatusReport(models.Model):
    class Meta:
        verbose_name                = 'status report'
        verbose_name_plural         = 'status reports'
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

    objects                         = StatusReportManager.from_queryset(StatusReportQuerySet)()

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
                                        related_name        = 'reports',
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
        return f"[{self.timestamp}] {self.station.code} {self.status}"
