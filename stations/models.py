import textwrap
from astropy.coordinates import EarthLocation
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

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

    def __str__(self):
        return "{name} ({subnetwork})".format(
            name        = self.name,
            subnetwork  = self.subnetwork,
        )

    def asDict(self):
        return {
            'latitude':     self.latitude,
            'longitude':    self.longitude,
            'altitude':     self.altitude,
            'founded':      self.founded,
            'address':      self.address,
        }

    def earthLocation(self):
        return EarthLocation.from_geodetic(self.longitude, self.latitude, self.altitude)

    def lastSighting(self):
        try:
            last = Sighting.objects.filter(station__id = self.id).latest('lightmaxTime')
            return last
        except ObjectDoesNotExist:
            return None

    def last10(self):
        last10 = Sighting.objects.filter(station_id = self.id).order_by('-lightmaxTime')[0:10]
        return last10
    
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
        return textwrap.shorten(self.text, 50, placeholder = '...')
