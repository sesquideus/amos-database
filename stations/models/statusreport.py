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
from meteors.models import Sighting


class StatusReport(models.Model):
    class Meta:
        verbose_name                = 'status report'
        verbose_name_plural         = 'status reports'

    timestamp                       = models.DateTimeField(
                                        verbose_name        = 'timestamp',
                                        auto_now            = True,
                                    )
    received                        = models.DateTimeField(
                                        verbose_name        = 'received at',
                                        auto_now_add        = True,
                                    )

    station                         = models.ForeignKey(
                                        'Station',
                                        on_delete           = models.CASCADE,
                                    )
    status                          = models.CharField(
                                        max_length          = 64,
                                    )

    def __str__(self):
        return f"{self.station.name} was {self.status} at {self.timestamp}"
