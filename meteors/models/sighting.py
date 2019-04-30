import datetime
import math
import pytz
import numpy as np
from pprint import pprint as pp

from django.db import models
from django.db.models import Max, Min
from django.contrib import admin
from django.urls import reverse
from django.utils.decorators import method_decorator

from astropy.coordinates import EarthLocation, SkyCoord, AltAz, get_sun, get_moon
from astropy.time import Time
from astropy import units

import core.models
from core.models import noneIfError

class SightingManager(models.Manager):
    
    """
        Reverse observation: create a sighting from a Meteor instance in the database.
        Currently a mockup!!! Does not calculate anything, generates numbers randomly to populate the rows.
    """
    def createForMeteor(self, meteor, station, **kwargs):
        print(f"Creating a sighting for meteor {meteor}, station {station}")
        sighting = self.create(
            beginningAzimuth    = np.random.uniform(0, 360),
            beginningAltitude   = np.degrees(np.arcsin(np.random.uniform(0, 1))),
            beginningTime       = meteor.beginningTime,

            lightmaxAzimuth     = np.random.uniform(0, 360),
            lightmaxAltitude    = np.degrees(np.arcsin(np.random.uniform(0, 1))),
            lightmaxTime        = meteor.lightmaxTime,

            endAzimuth          = np.random.uniform(0, 360),
            endAltitude         = np.degrees(np.arcsin(np.random.uniform(0, 1))),
            endTime             = meteor.endTime,
            
            angularSpeed        = np.random.normal(0, 30),
            magnitude           = -2.5 * np.log(np.random.pareto(2) * 10) + 5,

            meteor              = meteor,
            station             = station,
        )


class Sighting(models.Model):
    class Meta:
        verbose_name                = "meteor sighting"
        ordering                    = ['timestamp']

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

    solarElongation                 = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "solar elongation",
                                    )
    lunarElongation                 = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "lunar elongation",
                                    )
    
    def __str__(self):
        return f"{self.id} ({self.timestamp} from {self.station})"

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

    @method_decorator(noneIfError(AttributeError))
    def lightmaxTime(self):
        return self.lightmaxFrame().timestamp
    lightmaxTime.short_description = "timestamp at light-max"

    @method_decorator(noneIfError(AttributeError))
    def lightmaxMagnitude(self):
        return self.lightmaxFrame().magnitude
    lightmaxMagnitude.short_description = "apparent magnitude"

    @method_decorator(noneIfError(AttributeError))
    def lightmaxAltitude(self):
        return self.lightmaxFrame().altitude
    lightmaxAltitude.short_description = "altitude at light-max"

    @method_decorator(noneIfError(AttributeError))
    def lightmaxAzimuth(self):
        return self.lightmaxFrame().azimuth
    lightmaxAzimuth.short_description = "azimuth at light-max"

    def duration(self):
        try:
            return (self.firstFrame().timestamp - self.lastFrame().timestamp).total_seconds()
        except AttributeError:
            return None

    @method_decorator(noneIfError(AttributeError))
    def distance(self):
        obsLoc = self.station.earthLocation()
        metLoc = self.meteor.earthLocation()
        return np.sqrt((obsLoc.x - metLoc.x)**2 + (obsLoc.y - metLoc.y)**2 + (obsLoc.z - metLoc.z)**2).to(units.km).round(1)

    @method_decorator(noneIfError(AttributeError))
    def skyCoord(self):
        return AltAz(
            alt         = self.lightmaxFrame().altitude * units.degree,
            az          = self.lightmaxFrame().azimuth * units.degree,
            location    = self.station.earthLocation(),
            obstime     = Time(self.lightmaxFrame().timestamp)
        )

    def arcLength(self):
        first = self.firstFrame()
        last = self.lastFrame()
        phi1 = math.radians(first.altitude)
        phi2 = math.radians(last.altitude)
        lambda1 = math.radians(first.azimuth)
        lambda2 = math.radians(last.azimuth)
        return math.degrees(math.acos(math.sin(phi1) * math.sin(phi2) + math.cos(phi1) * math.cos(phi2) * math.cos(lambda1 - lambda2)))

    def previous(self):
        try:
            return Sighting.objects.exclude(timestamp__isnull = True).filter(timestamp__lt = self.timestamp).latest('timestamp').id
        except Sighting.DoesNotExist:
            return Sighting.objects.latest('timestamp').id

    def next(self):
        try:
            return Sighting.objects.exclude(timestamp__isnull = True).filter(timestamp__gt = self.timestamp).earliest('timestamp').id
        except Sighting.DoesNotExist:
            return Sighting.objects.earliest('timestamp').id

    def coordAltAz(self):
        return AltAz(obstime = Time(self.lightmaxFrame().timestamp), location = self.station.earthLocation())

    def getSun(self):
        frame = self.lightmaxFrame()
        if frame is None or frame.timestamp is None or self.coordAltAz is None:
            return None

        return get_sun(Time(self.lightmaxFrame().timestamp)).transform_to(self.coordAltAz())

    def getMoon(self):
        frame = self.lightmaxFrame()
        if frame is None or frame.timestamp is None or self.coordAltAz is None:
            return None

        return get_moon(Time(self.lightmaxFrame().timestamp)).transform_to(self.coordAltAz())

    @method_decorator(noneIfError(AttributeError, TypeError))
    def getSolarElongation(self):
        return self.getSun().separation(self.skyCoord()).degree
    
    @method_decorator(noneIfError(AttributeError, TypeError))
    def getLunarElongation(self):
        return self.getMoon().separation(self.skyCoord()).degree

    def getSunInfo(self):
        sun = self.getSun()
        elong = self.getSolarElongation()
        return {
            'coord': sun,
            'elong': elong,
        }

    def getMoonInfo(self):
        moon = self.getMoon()
        elong = self.getLunarElongation()
        return {
            'coord': moon,
            'elong': elong,
        }


    def save(self, *args, **kwargs):
        try:
            self.solarElongation = self.getSolarElongation()
        except (TypeError, AttributeError):
            self.solarElongation = None
        
        try:
            self.lunarElongation = self.getLunarElongation()
        except (TypeError, AttributeError):
            self.lunarElongation = None
        super().save(*args, **kwargs)
