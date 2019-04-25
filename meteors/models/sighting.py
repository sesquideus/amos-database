import datetime
import math
import pytz
import numpy as np
from pprint import pprint as pp

from django.db import models
from django.db.models import Max, Min
from django.contrib import admin
from django.urls import reverse

from astropy.coordinates import EarthLocation, SkyCoord, AltAz, get_sun, get_moon
from astropy.time import Time
from astropy import units

import core.models
from .frame import Frame

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
    timestamp                      = models.DateTimeField(
                                        verbose_name        = "timestamp",
                                    )
    magnitude                       = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "apparent magnitude",
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
        return f"{self.timestamp} from {self.station}"

    def get_absolute_url(self):
        return reverse('sighting', kwargs = {'id': self.id})


    # frame shortcuts

    def firstFrame(self):
        return self.frames.earliest('timestamp')

    def lightmaxFrame(self):
        return self.frames.order_by('-magnitude').first()

    def lastFrame(self):
        return self.frames.latest('timestamp')

    def lightmaxTime(self):
        try:
            return self.lightmaxFrame().timestamp
        except AttributeError:
            return None

    def lightmaxAltitude(self):
        try:
            return self.lightmaxFrame().altitude
        except AttributeError:
            return None

    def lightmaxAzimuth(self):
        try:
            return self.lightmaxFrame().azimuth
        except AttributeError:
            return None

    # 
    
    #def timestamp(self):
    #    return "<unknown time>" if self.lightmaxTime is None else self.lightmaxTime.strftime("%Y-%m-%d %H:%M:%S.%f")

    def duration(self):
        try:
            return (self.firstFrame.timestamp - self.lastFrame.timestamp).total_seconds()
        except AttributeError:
            return None

    def distance(self):
        try:
            obsLoc = self.station.earthLocation()
            metLoc = self.meteor.earthLocation()
            return np.sqrt((obsLoc.x - metLoc.x)**2 + (obsLoc.y - metLoc.y)**2 + (obsLoc.z - metLoc.z)**2).to(units.km).round(1)
        except AttributeError:
            return None

    def skyCoord(self):
        try:
            return AltAz(
                alt         = self.lightmaxFrame().altitude * units.degree,
                az          = self.lightmaxFrame().azimuth * units.degree,
                location    = self.station.earthLocation(),
                obstime     = Time(self.lightmaxFrame().timestamp)
            )
        except TypeError:
            return None

    def arcLength(self):
        try:
            first = self.firstFrame()
            last = self.lastFrame()
            phi1 = math.radians(first.altitude)
            phi2 = math.radians(last.altitude)
            lambda1 = math.radians(first.azimuth)
            lambda2 = math.radians(last.azimuth)
            return math.degrees(math.acos(math.sin(phi1) * math.sin(phi2) + math.cos(phi1) * math.cos(phi2) * math.cos(lambda1 - lambda2)))
        except TypeError:
            return None

    def previous(self):
        try:
            result = Sighting.objects.filter(timestamp__lt = self.timestamp).latest('timestamp').id
        except Sighting.DoesNotExist:
            result = Sighting.objects.latest('timestamp').id
        return result

    def next(self):
        try:
            result = Sighting.objects.filter(timestamp__lt = self.timestamp).earliest('timestamp').id
        except Sighting.DoesNotExist:
            result = Sighting.objects.earliest('timestamp').id
        return result

    def coordAltAz(self):
        return AltAz(obstime = Time(self.lightmaxFrame().timestamp), location = self.station.earthLocation())

    def getSun(self):
        if self.lightmaxFrame() is None:
            return None
        try:
            return get_sun(Time(self.lightmaxFrame().timestamp)).transform_to(self.coordAltAz())
        except TypeError:
            return None

    def getMoon(self):
        if self.lightmaxFrame() is None:
            return None
        try:
            return get_moon(Time(self.lightmaxFrame().timestamp)).transform_to(self.coordAltAz())
        except TypeError:
            return None

    def getSolarElongation(self):
        try:
            return self.getSun().separation(self.skyCoord())
        except (TypeError, AttributeError):
            return None
    
    def getLunarElongation(self):
        try:
            return self.getMoon().separation(self.skyCoord())
        except (TypeError, AttributeError):
            return None

    def getSunInfo(self):
        sun = self.getSun()
        elong = self.getSolarElongation()

        return {
            'coord': sun,
            'elong': None if elong is None else elong.degree,
        }

    def getMoonInfo(self):
        moon = self.getMoon()
        elong = self.getLunarElongation()

        return {
            'coord': moon,
            'elong': None if elong is None else elong.degree,
        }


    def save(self, *args, **kwargs):
        try:
            self.solarElongation = self.getSolarElongation().degree
        except (TypeError, AttributeError):
            self.solarElongation = None
        
        try:
            self.lunarElongation = self.getLunarElongation().degree
        except (TypeError, AttributeError):
            self.lunarElongation = None
        super().save(*args, **kwargs)
