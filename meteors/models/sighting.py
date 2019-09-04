import datetime
import math
import numpy as np

from django.db import models
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
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


class Sighting(models.Model):
    class Meta:
        verbose_name                = "meteor sighting"
        ordering                    = ['timestamp']
        get_latest_by               = 'timestamp'

    objects                         = SightingManager()

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

    angularSpeed                    = models.FloatField(
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
                                        on_delete           = models.SET_NULL,
                                    )



    def __str__(self):
        meteor = 'unknown meteor' if self.meteor is None else self.meteor.name
        return f"#{self.id} ({meteor} at {self.timestamp} from {self.station})"

    def get_absolute_url(self):
        return reverse('sighting', kwargs = {'id': self.id})

    # frame shortcuts

    def firstFrame(self):
        return self.frames.earliest('timestamp')
    firstFrame.short_description = "first frame"

    def lightmaxFrame(self):
        return self.frames.order_by('magnitude').first()
    lightmaxFrame.short_description = "brightest frame"

    def lastFrame(self):
        return self.frames.latest('timestamp')
    lastFrame.short_description = "last frame"

    def frameCount(self):
        return self.frames.count()
    frameCount.short_description = "frame count"

    def lightmaxTime(self):
        if self.lightmaxFrame() is not None:
            return self.lightmaxFrame().timestamp
        return None
    lightmaxTime.short_description = "timestamp at light-max"

    def lightmaxMagnitude(self):
        if self.lightmaxFrame() is not None:
            return self.lightmaxFrame().magnitude
        return None
    lightmaxMagnitude.short_description = "apparent magnitude"

    def lightmaxAltitude(self):
        if self.lightmaxFrame() is not None:
            return self.lightmaxFrame().altitude
        return None
    lightmaxAltitude.short_description = "altitude at light-max"

    def lightmaxAzimuth(self):
        if self.lightmaxFrame() is not None:
            return self.lightmaxFrame().azimuth
        return None
    lightmaxAzimuth.short_description = "azimuth at light-max"

    def duration(self):
        try:
            return (self.firstFrame().timestamp - self.lastFrame().timestamp).total_seconds()
        except AttributeError:
            return None

    def arcLength(self):
        first = self.firstFrame()
        last = self.lastFrame()
        phi1 = math.radians(first.altitude)
        phi2 = math.radians(last.altitude)
        lambda1 = math.radians(first.azimuth)
        lambda2 = math.radians(last.azimuth)
        return math.degrees(math.acos(math.sin(phi1) * math.sin(phi2) + math.cos(phi1) * math.cos(phi2) * math.cos(lambda1 - lambda2)))

    @method_decorator(noneIfError(ObjectDoesNotExist))
    def previous(self):
        return Sighting.objects.exclude(timestamp__isnull = True).filter(timestamp__lt = self.timestamp).latest('timestamp').id

    @method_decorator(noneIfError(ObjectDoesNotExist))
    def next(self):
        return Sighting.objects.exclude(timestamp__isnull = True).filter(timestamp__gt = self.timestamp).earliest('timestamp').id
