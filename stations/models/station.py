import textwrap
import datetime
import dotmap
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
from . import Country


class Station(core.models.NamedModel):
    class Meta:
        verbose_name                = 'station'
        ordering                    = ['name']

    code                            = models.CharField(
                                        max_length          = 8,
                                        unique              = True,
                                        help_text           = "a simple unique code (2-4 uppercase letters)",
                                    )

    subnetwork                      = models.ForeignKey(
                                        'Subnetwork',
                                        null                = True,
                                        blank               = True,
                                        on_delete           = models.CASCADE, 
                                        related_name        = 'stations',
                                    )
    country                         = models.ForeignKey(
                                        'Country',
                                        on_delete           = models.CASCADE,
                                    )

    latitude                        = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "latitude",
                                        help_text           = "[-90°, 90°], north positive",
                                    )
    longitude                       = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "longitude",
                                        help_text           = "[-180°, 180°], east positive",
                                    )
    altitude                        = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "altitude",
                                        help_text           = "metres above mean sea level",
                                    )

    address                         = models.CharField(
                                        null                = True,
                                        blank               = True,
                                        max_length          = 256,
                                        help_text           = "printable full address",
                                    )    
    founded                         = models.DateField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "founding date",
                                        help_text           = "date when the station was founded",
                                    ) 
    timezone                        = models.CharField(
                                        null                = False,
                                        blank               = False,
                                        max_length          = 64,
                                        choices             = zip(pytz.common_timezones, pytz.common_timezones),
                                        help_text           = "official timezone name",
                                    )


    def __str__(self):
        return "{name} ({subnetwork})".format(
            name        = self.name,
            subnetwork  = self.subnetwork,
        )

    def get_absolute_url(self):
        return reverse('station', kwargs = {'code': self.code})

    def asDict(self):
        return {
            'latitude':     self.latitude,
            'longitude':    self.longitude,
            'altitude':     self.altitude,
            'founded':      self.founded,
            'address':      self.address,
        }

    def dynamicDict(self):
        return {
            'sun':          self.sunPosition(),
        }

    def earthLocation(self):
        return EarthLocation.from_geodetic(self.longitude, self.latitude, self.altitude)

    def sunPosition(self, time = None):
        if time is None:
            time = datetime.datetime.now()

        loc = AltAz(obstime = Time(time), location = self.earthLocation())
        sun = get_sun(Time(time)).transform_to(loc)

        return {
            'alt':  sun.altaz.alt.degree,
            'az':   sun.altaz.az.degree,
        }

    def lastSighting(self):
        try:
            return Sighting.objects.filter(station__id = self.id).latest('timestamp')
        except ObjectDoesNotExist:
            return None

    def location(self):
        return "{latitude:.6f}° {latNS}, {longitude:.6f}° {lonEW}, {altitude:.0f} m".format(
            latitude    = self.latitude,
            latNS       = 'N' if self.latitude >= 0 else 'S',
            longitude   = self.longitude,
            lonEW       = 'E' if self.longitude >= 0 else 'W',
            altitude    = self.altitude,
        )

    def currentStatus(self):
        try:
            lastReport = self.reports.latest()
        except ObjectDoesNotExist:
            return {
                'id':       'noreports',
                'short':    "no status reports",
                'long':     "The station has never sent any reports",
            }

        if (datetime.datetime.now(pytz.utc) - lastReport.timestamp).total_seconds() > 180:
            return {
                'id':       'timeout',
                'short':    "timeout",
                'long':     f"The station has not sent a report since {self.reports.latest().timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            }
        else:
            return {
                'id':       'ok',
                'short':    "OK",
                'long':     "The station is working correctly",
            }

    def json(self):
        return {
            'id':       self.id,
            'code':     self.code,
            'name':     self.name,
            'status':   self.currentStatus(),
        }

