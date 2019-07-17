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
from . import Station
from meteors.models import Sighting


class StatusReportManager(models.Manager):
    def createFromPOST(self, **kwargs):
        report = self.create(
            timestamp       = kwargs.get('timestamp'),
            station         = Station.objects.get(code = kwargs.get('station')),
            status          = kwargs.get('status'),
        )
        return report


class StatusReport(models.Model):
    class Meta:
        verbose_name                = 'status report'
        verbose_name_plural         = 'status reports'
        get_latest_by               = ['timestamp']
        indexes                     = [
                                        models.Index(fields = ['station', 'timestamp']),
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

    def __str__(self):
        return f"{self.station.name} was {self.status} at {self.timestamp}"
