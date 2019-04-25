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

class Country(core.models.NamedModel):
    class Meta:
        verbose_name                = 'country'
        verbose_name_plural         = 'countries'


class Subnetwork(core.models.NamedModel):
    class Meta:
        verbose_name                = 'subnetwork'
        ordering                    = ['id']
    
    founded                         = models.DateField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "founding date",
                                        help_text           = "date when the subnetwork was founded",
                                    ) 

    def count(self):
        return Station.objects.filter(subnetwork = self.id).count()
    count.short_description = 'Station count'

    def centre(self):
        stations = self.station_set.all()
        return {
            'latitude':     sum([station.latitude for station in stations]),
            'longitude':    sum([station.longitude for station in stations]),
        }

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
                                        help_text           = 'official timezone name',
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

    def register(self, meteor):
        return meteor.earthLocation() - self.earthLocation()

    def location(self):
        return "{latitude:.6f}° {latNS}, {longitude:.6f}° {lonEW}, {altitude:.1f} m".format(
            latitude    = self.latitude,
            latNS       = 'N' if self.latitude >= 0 else 'S',
            longitude   = self.longitude,
            lonEW       = 'E' if self.longitude >= 0 else 'W',
            altitude    = self.altitude,
        )

    def observe(self, meteor):
        (x, y, z) = self.earthLocation().to_geocentric()
        (a, b, c) = meteor.earthLocation().to_geocentric()
        diff = EarthLocation.from_geocentric()
        print(difference)

class LogEntry(models.Model):
    class Meta:
        verbose_name                = 'log entry'
        verbose_name_plural         = 'log entries'
        ordering                    = ['created']

    station                         = models.ForeignKey(
                                        'Station',
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "station",
                                        help_text           = "the station in question",
                                        on_delete           = models.CASCADE,
                                    )
    text                            = models.TextField(
                                        help_text           = "text of the log entry",
                                    )
    created                         = models.DateTimeField(
                                        auto_now_add        = True,
                                    )
    updated                         = models.DateTimeField(
                                        auto_now            = True,
                                    )

    def __str__(self):
        return "[{}] {}".format(
            self.created.strftime('%Y-%m-%d %H:%M:%S'),
            textwrap.shorten(self.text, 50, placeholder = '...'),
        )
