import datetime
import pytz

from django.db import models
from django.db.models import Prefetch, F, Q, OuterRef, Max, Count
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from astropy.coordinates import EarthLocation, AltAz, get_sun, get_moon
from astropy.time import Time

import core.models
from meteors.models import Sighting
from stations.models.heartbeat import Heartbeat

from core.templatetags.quantities import since_date_time


class StationQuerySet(models.QuerySet):
    def with_last_sighting(self):
        latest = Sighting.objects.order_by('station__id', '-timestamp').distinct('station__id')
        return self.prefetch_related(
            Prefetch(
                'sightings',
                queryset=Sighting.objects.filter(id__in=latest),
                to_attr='last_sighting',
            )
        )

    def with_last_heartbeat(self):
        latest = Heartbeat.objects.order_by('station__id', '-timestamp').distinct('station__id')
        return self.prefetch_related(
            Prefetch(
                'heartbeats',
                queryset=Heartbeat.objects.filter(id__in=latest),
                to_attr='last_heartbeat',
            )
        )

    def with_log_entries(self):
        return self.prefetch_related('log_entries')

    def with_subnetwork(self):
        return self.select_related('subnetwork')

    def with_graph(self):
        return self.prefetch_related(
            Prefetch(
                'heartbeats',
                queryset=Heartbeat.objects.for_graph(),
                to_attr='heartbeats_graph',
            )
        )


class Station(core.models.NamedModel):
    class Meta:
        verbose_name                = 'station'
        app_label                   = 'stations'
        ordering                    = ['name']
        constraints                 = [
                                        models.CheckConstraint(
                                            check=Q(
                                                latitude__gte=-90,
                                                latitude__lte=90,
                                                longitude__gte=-180,
                                                longitude__lte=180,
                                            ),
                                            name='coordinates',
                                        )
                                    ]

    objects                         = StationQuerySet.as_manager()

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
    on                              = models.BooleanField(
                                        null                = False,
                                        default             = False,
                                    )

    picture                         = models.ImageField(
                                        upload_to           = 'stations/',
                                        null                = True,
                                        blank               = True,
                                    )

    def __str__(self):
        return f"{self.name} ({self.subnetwork.name})"

    def get_absolute_url(self):
        return reverse('station', kwargs = {'code': self.code})

    def as_dict(self):
        return {
            'latitude':     self.latitude,
            'longitude':    self.longitude,
            'altitude':     self.altitude,
            'founded':      self.founded,
            'address':      self.address,
        }

    def dynamic_dict(self):
        return {
            'sun':          self.sun_position(),
        }

    def earth_location(self):
        return EarthLocation.from_geodetic(self.longitude, self.latitude, self.altitude)

    def alt_az(self, time=None):
        if time is None:
            time = datetime.datetime.now()

        return AltAz(
            obstime=Time(time),
            location=self.earth_location()
        )

    def sun_position(self, time=None):
        if time is None:
            time = datetime.datetime.now()

        sun = get_sun(Time(time)).transform_to(self.alt_az(time))

        return {
            'alt':  sun.altaz.alt.degree,
            'az':   sun.altaz.az.degree,
        }

    def moon_position(self, time=None):
        if time is None:
            time = datetime.datetime.now()

        moon = get_moon(Time(time)).transform_to(self.alt_az(time))

        return {
            'alt':  moon.altaz.alt.degree,
            'az':   moon.altaz.az.degree,
        }

    def location(self):
        return "{latitude:.6f}° {latNS}, {longitude:.6f}° {lonEW}, {altitude:.0f} m".format(
            latitude    = abs(self.latitude),
            latNS       = 'N' if self.latitude >= 0 else 'S',
            longitude   = abs(self.longitude),
            lonEW       = 'E' if self.longitude >= 0 else 'W',
            altitude    = self.altitude,
        )

    def get_current_status(self):
        try:
            last_heartbeat = self.last_heartbeat[0]
            time_since = (datetime.datetime.now(pytz.utc) - last_heartbeat.timestamp).total_seconds()
        except (IndexError, AttributeError):
            return StatusEmpty()

        if not self.on:
            return StatusOff(last_heartbeat)

        if time_since > 120:
            return StatusTimeout(last_heartbeat)
        else:
            return StatusOK(last_heartbeat)

    def json(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'status': self.get_current_status().short,
            'sun-alt': self.sun_position()['alt'],
            'sun-az': self.sun_position()['az'],
        }


class Status():
    def __init__(self, last_report=None):
        if last_report is not None:
            self.last_report = last_report

    def age(self):
        return datetime.datetime.now(tz=pytz.UTC) - self.last_report.timestamp

    def toJSON(self):
        return {
            'code': self.code,
            'short': self.short,
            'description': self.get_description(),
        }


class StatusOK(Status):
    code = 'ok'
    short = 'OK'

    def get_description(self):
        return f"The station is working normally. Last report on {self.last_report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}."


class StatusEmpty(Status):
    code = 'none'
    short = 'no reports'

    def get_description(self):
        return "The station has never sent any reports."

    def age(self):
        return None


class StatusTimeout(Status):
    code = 'timeout'
    short = 'timeout'

    def get_description(self):
        timestamp = self.last_report.timestamp
        return (f"The station seems to be offline. " +
            f"No reports received since {timestamp.strftime('%Y-%m-%d %H:%M:%S')} " +
            f"({since_date_time(timestamp)})")


class StatusOff(Status):
    code = 'off'
    short = 'off'

    def get_description(self):
        return f"The station has been turned off. Last report on {self.last_report.timestamp}"
