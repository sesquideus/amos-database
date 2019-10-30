import datetime
import math
import numpy as np

from django.db import models
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch, F, Q, Value, Window, Min
from django.db.models.functions import Coalesce, Lead
from django.urls import reverse
from django.utils.decorators import method_decorator

from astropy.coordinates import AltAz, get_sun, get_moon
from astropy.time import Time
from astropy import units

from pprint import pprint as pp

from core.models import noneIfError
from meteors.models import Frame



class SightingManager(models.Manager):
    """
        Reverse observation: create a sighting from a Meteor instance in the database.
        Currently a mockup!!! Does not calculate anything, generates numbers randomly to populate the rows.
    """
    def createForMeteor(self, meteor, station, **kwargs):
        print(f"Creating a sighting for meteor {meteor}, station {station}")
        
        Station = apps.get_model('stations', 'Station')
        sighting = self.create(
            timestamp           = meteor.timestamp,
            angularSpeed        = np.random.normal(0, 30),
            meteor              = meteor,
            station             = Station.objects.get(code = station),
        )

        time = meteor.timestamp
        alt0 = np.degrees(np.arcsin(np.random.random()))
        az0 = np.random.random() * 360.0
        dalt = np.random.normal(0, 3)
        daz = np.random.normal(0, 3)

        mag = 6 - 3 * np.random.pareto(2.3)
        cnt = int(np.floor(np.random.pareto(1.3) + 5))

        print(f"Adding {cnt} frames")
        for x in np.arange(0, cnt):
            mag = mag + np.random.random() if np.random.random() < x / cnt else mag - np.random.random()
            Frame.objects.create(
                timestamp   = time + datetime.timedelta(seconds = x * 0.05),
                sighting    = sighting,
                order       = x,
                x           = np.random.randint(0, 1600),
                y           = np.random.randint(0, 1200),
                altitude    = alt0 + x * dalt,
                azimuth     = az0 + x * daz,
                magnitude   = mag,
            )

    """
        Create a new Sighting from data received at the POST endpoint.
    """
    def createFromPOST(self, stationCode, **kwargs):
        print(f"Creating a sighting from POST at station {stationCode}")
        pp(kwargs)
        
        Station = apps.get_model('stations', 'Station')
        sighting = self.create(
            timestamp           = datetime.datetime.strptime(kwargs.get('timestamp'), '%Y-%m-%d %H:%M:%S.%f%z'),
            angularSpeed        = kwargs.get('angularSpeed'),
            meteor              = None,
            station             = Station.objects.get(code = stationCode),
        )

        for order, frame in enumerate(kwargs.get('frames')):
            Frame.objects.create(
                timestamp       = datetime.datetime.strptime(frame.get('timestamp'), '%Y-%m-%d %H:%M:%S.%f%z'),
                sighting        = sighting,
                order           = order,
                x               = 0,
                y               = 0,
                altitude        = frame.get('altitude'),
                azimuth         = frame.get('azimuth'),
                magnitude       = frame.get('magnitude'),
            )
        return sighting


class SightingQuerySet(models.QuerySet):
    def with_neighbours(self):
        return self.annotate(
            previous=Window(
                expression=Lead('timestamp', offset=1, default=None),
                order_by=F('timestamp').asc(),
            ),
            next=Window(
                expression=Lead('timestamp', offset=1, default=None),
                order_by=F('timestamp').desc(),
            ),
        )

    def with_frames(self):
        return self.prefetch_related(
            Prefetch(
                'frames',
                queryset=Frame.objects.with_flight_time(),
            )
        ).annotate(
            first=Value(Frame.objects.earliest('timestamp').id, output_field=models.IntegerField()),
            frame_lightmax=Window(
                expression=Min('frames__magnitude'),
                partition_by=[F('frames__sighting')],
            ),
            last=Value(Frame.objects.latest('timestamp').id, output_field=models.IntegerField()),
        )

    def for_station(self, station_id):
        return self.filter(
            Q(station__id=station_id)
        )

class Sighting(models.Model):
    class Meta:
        verbose_name                = "meteor sighting"
        ordering                    = ['timestamp']
        get_latest_by               = 'timestamp'

    objects                         = SightingQuerySet.as_manager()

    id                              = models.AutoField(
                                        primary_key         = True,
                                        verbose_name        = "ID",
                                    )
    timestamp                       = models.DateTimeField(
                                        verbose_name        = "timestamp",
                                    )

    composite                       = models.ImageField(
                                        upload_to           = 'sightings/',
                                        null                = True,
                                        blank               = True,
                                    )

    angular_speed                   = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "observed angular speed [°/s]",
                                    )
    meteor                          = models.ForeignKey(
                                        'Meteor',
                                        null                = True,
                                        blank               = True,
                                        related_name        = 'sightings',
                                        on_delete           = models.SET_NULL,
                                    )
    station                         = models.ForeignKey(
                                        'stations.Station',
                                        null                = True,
                                        verbose_name        = "station",
                                        related_name        = 'sightings',
                                        on_delete           = models.SET_NULL,
                                    )

    def __str__(self):
        meteor = 'unknown meteor' if self.meteor is None else self.meteor.name
        return f"#{self.id} ({meteor} at {self.timestamp} from {self.station})"

    def get_absolute_url(self):
        return reverse('sighting', kwargs = {'id': self.id})

    # frame shortcuts

    def arcLength(self):
        first = self.firstFrame()
        last = self.lastFrame()
        phi1 = math.radians(first.altitude)
        phi2 = math.radians(last.altitude)
        lambda1 = math.radians(first.azimuth)
        lambda2 = math.radians(last.azimuth)
        return math.degrees(math.acos(math.sin(phi1) * math.sin(phi2) + math.cos(phi1) * math.cos(phi2) * math.cos(lambda1 - lambda2)))
