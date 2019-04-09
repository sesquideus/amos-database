from django.db import models
from django.db.models import Max, Min
from django.contrib import admin
from django.urls import reverse

from astropy.coordinates import EarthLocation, SkyCoord, AltAz, get_sun, get_moon
from astropy.time import Time
from astropy import units

import core.models

import datetime
import math
import pytz
import numpy as np
from pprint import pprint as pp

class SightingManager(models.Manager):
    
    """
        Reverse observation: create a sighting from a Meteor instance in the database.
        Currently a mockup!!! Does not calculate anything, generates numbers randomly to populate the rows.
    """
    def createForMeteor(self, meteor, station):
        print(f"Creating for meteor {meteor}, station {station}")
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
        ordering                    = ['lightmaxTime']

    objects                         = SightingManager()

    id                              = models.AutoField(
                                        primary_key         = True,
                                        verbose_name        = "ID",
                                    )
    magnitude                       = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "apparent magnitude",
                                    )
    
    beginningAltitude               = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "altitude at beginning",
                                    )
    beginningAzimuth                = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "azimuth at beginning",
                                    )
    beginningTime                   = models.DateTimeField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "time of beginning",
                                    )

    lightmaxAltitude                = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "altitude at max light",
                                    )
    lightmaxAzimuth                 = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "azimuth at max light",
                                    )
    lightmaxTime                    = models.DateTimeField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "timestamp at max light",
                                    )

    endAltitude                     = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "altitude at end",
                                    )
    endAzimuth                      = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "azimuth at end",
                                    )
    endTime                         = models.DateTimeField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "timestamp at end",
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
        return f"{self.timestamp()} from {self.station}"

    def timestamp(self):
        return "<unknown time>" if self.lightmaxTime is None else self.lightmaxTime.strftime("%Y-%m-%d %H:%M:%S.%f")

    def get_absolute_url(self):
        return reverse('sighting', kwargs = {'id': self.id})

    def imageFile(self):
        return f"M-{self.station.code}-{self.lightmaxTime.strftime('%Y-%m-%dT%H-%M-%S')}P.jpg" if self.lightmaxTime else None

    def duration(self):
        return self.endTime - self.beginningTime if self.endTime != None and self.beginningTime != None else None

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
                alt         = self.lightmaxAltitude * units.degree,
                az          = self.lightmaxAzimuth * units.degree,
                location    = self.station.earthLocation(),
                obstime     = Time(self.lightmaxTime)
            )
        except TypeError:
            return None

    def arcLength(self):
        try:
            phi1 = math.radians(self.beginningAltitude)
            phi2 = math.radians(self.endAltitude)
            lambda1 = math.radians(self.beginningAzimuth)
            lambda2 = math.radians(self.endAzimuth)
            return math.degrees(math.acos(math.sin(phi1) * math.sin(phi2) + math.cos(phi1) * math.cos(phi2) * math.cos(lambda1 - lambda2)))
        except TypeError:
            return None

    def airMass(self):
        try:
            return 1 / math.sin(math.radians(self.lightmaxAltitude))
        except TypeError:
            return None

    def previous(self):
        try:
            result = Sighting.objects.filter(lightmaxTime__lt = self.lightmaxTime).order_by('-lightmaxTime')[0:1].get().id
        except Sighting.DoesNotExist:
            result = Sighting.objects.order_by('lightmaxTime').last().id
        return result

    def next(self):
        try:
            result = Sighting.objects.filter(lightmaxTime__gt = self.lightmaxTime).order_by('lightmaxTime')[0:1].get().id
        except Sighting.DoesNotExist:
            result = Sighting.objects.order_by('lightmaxTime').first().id
        return result

    def coordAltAz(self):
        return AltAz(obstime = Time(self.lightmaxTime), location = self.station.earthLocation())

    def getSun(self):
        try:
            return get_sun(Time(self.lightmaxTime)).transform_to(self.coordAltAz())
        except TypeError:
            return None

    def getMoon(self):
        try:
            return get_moon(Time(self.lightmaxTime)).transform_to(self.coordAltAz())
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
        return {
            'coord': sun,
            'elong': self.getSolarElongation(),
        }

    def getMoonInfo(self):
        moon = self.getMoon()
        return {
            'coord': moon,
            'elong': self.getLunarElongation(),
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
        super(Sighting, self).save(*args, **kwargs)
