import textwrap
import datetime
import pytz
from django.db import models
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator

from astropy.coordinates import EarthLocation, SkyCoord, AltAz, get_sun, get_moon
from astropy.time import Time
from astropy import units

import core.models
#from stations.models.station import Station
from meteors.models import Sighting


class StatusReportManager(models.Manager):
    def createFromPOST(self, stationCode, **kwargs):
        report = self.create(
            timestamp       = kwargs.get('timestamp'),
            #station         = Station.objects.get(code = stationCode),
            status          = kwargs.get('status'),
            lid             = kwargs.get('lid'),
            heating         = kwargs.get('heating'),
            temperature     = kwargs.get('temperature'),
            pressure        = kwargs.get('pressure'),
            humidity        = kwargs.get('humidity'),
        )
        return report


class StatusReport(models.Model):
    class Meta:
        verbose_name                = 'status report'
        verbose_name_plural         = 'status reports'
        get_latest_by               = ['timestamp']
        indexes                     = [
                                        models.Index(fields=['station', 'timestamp']),
                                    ]

    LID_STATES                      = [
                                        ('O', 'open'),
                                        ('C', 'closed'),
                                        ('P', 'problem'),
                                    ]
    HEATING_STATES                  = [
                                        ('1', 'on'),
                                        ('0', 'off'),
                                        ('P', 'problem'),
                                    ]

    objects                         = StatusReportManager()

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
                                        max_length          = 64,
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
