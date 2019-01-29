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
import numpy as np

class MeteorManager(models.Manager):
    def createRandom(self):
        timestamp = datetime.datetime.utcnow()
        meteor = self.create(
            timestamp           = timestamp,
            lightmaxTime        = timestamp,
            magnitude           = -2.5 * np.log(np.random.pareto(2) * 10),
            lightmaxLatitude    = np.random.uniform(20, 60),
            lightmaxLongitude   = np.random.uniform(-20, 30),
            lightmaxAltitude    = np.random.normal(80000, 15000),
            velocityX           = np.random.normal(0, 20000),
            velocityY           = np.random.normal(0, 20000),
            velocityZ           = np.random.normal(0, 20000),
        )
        return meteor

class Meteor(models.Model):
    class Meta:
        verbose_name                = "meteor"
        ordering                    = ['timestamp']

    objects                         = MeteorManager()
        
    id                              = models.AutoField(
                                        primary_key         = True,
                                        verbose_name        = "ID",
                                    )
    timestamp                       = models.DateTimeField(
                                        unique              = True,
                                    )

    magnitude                       = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "absolute magnitude",
                                    )
    source                          = models.ForeignKey(
                                        'Shower',
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "meteor shower",
                                        on_delete           = models.SET_NULL,
                                    )    

    beginningLatitude               = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "latitude of trail beginning",
                                    )
    beginningLongitude              = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "longitude of trail beginning",
                                    )
    beginningAltitude               = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "altitude of trail beginning",
                                    )   
    beginningTime                   = models.DateTimeField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "timestamp of trail beginning",
                                    )
    
    lightmaxLatitude                = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "latitude at max light",
                                    )
    lightmaxLongitude               = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "longitude at maxlight",
                                    )
    lightmaxAltitude                = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "altitude at maxlight",
                                    )   
    lightmaxTime                    = models.DateTimeField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "timestamp at maxlight",
                                    )


    endLatitude                     = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "latitude of trail end",
                                    )
    endLongitude                    = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "longitude of trail end",
                                    )
    endAltitude                     = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "altitude of trail end",
                                    )   
    endTime                         = models.DateTimeField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "timestamp of trail end",
                                    )

    velocityX                       = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "geocentric velocity at infinity, x"
                                    )
    velocityY                       = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "geocentric velocity at infinity, y"
                                    )
    velocityZ                       = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "geocentric velocity at infinity, z"
                                    )

    def __str__(self):
        return "{time}".format(
            time = self.timestamp.strftime("%Y%m%d-%H%M%S-%f"),
        )

    def get_absolute_url(self):
        return reverse('meteor', kwargs = {'id': self.id})

    def asDict(self):
        return {
            'latitude': self.lightmaxLatitude,
            'longitude': self.lightmaxLongitude,
            'altitude': self.lightmaxAltitude,
            'magnitude': self.magnitude,
        }

    def earthLocation(self):
        try:
            result = EarthLocation.from_geodetic(self.lightmaxLongitude * units.deg, self.lightmaxLatitude * units.deg, self.lightmaxAltitude * units.m)
        except TypeError:
            result = None
        return result

    def previous(self):
        try:
            result = Meteor.objects.filter(lightmaxTime__lt = self.lightmaxTime).order_by('-lightmaxTime')[0:1].get().id
        except Meteor.DoesNotExist:
            result = Meteor.objects.order_by('lightmaxTime').last().id
        return result

    def next(self):
        try:
            result = Meteor.objects.filter(lightmaxTime__gt = self.lightmaxTime).order_by('lightmaxTime')[0:1].get().id
        except Meteor.DoesNotExist:
            result = Meteor.objects.order_by('lightmaxTime').first().id
        return result

    def speed(self):
        try:
            return np.sqrt(self.velocityX**2 + self.velocityY**2 + self.velocityZ**2)
        except TypeError:
            return None

class Sighting(models.Model):
    class Meta:
        verbose_name                = "meteor sighting"
        ordering                    = ['lightmaxTime']

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
                                        verbose_name        = "observed angular speed",
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
        return '{time} at ({az}, {elev})'.format(
            time    = '<unknown time>' if self.lightmaxTime is None else self.lightmaxTime.strftime("%Y-%m-%d %H:%M:%S.%f"),
            az      = '???' if self.lightmaxAzimuth is None else "{:.1f}°".format(self.lightmaxAzimuth),
            elev    = '???' if self.lightmaxAltitude is None else "{:.1f}°".format(self.lightmaxAltitude),
        )

    def get_absolute_url(self):
        return reverse('sighting', kwargs = {'id': self.id})

    def colour(self):
        ex = int((-self.magnitude + 5) * 10)
        return 'hsl(0, 0%, {:02d}%)'.format(max(0, min(ex, 100)))

    def colourText(self):
        ex = int((self.magnitude - 5) * 30)
        return '#{0:02X}{0:02X}{0:02X}'.format(min(64 + ex, 255))

    def image(self):
        return "M{}_AMOS5_P.jpg".format(self.lightmaxTime.strftime("%Y%m%d_%H%M%S")) if self.lightmaxTime else None

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
        except TypeError:
            return None
    
    def getLunarElongation(self):
        try:
            return self.getMoon().separation(self.skyCoord())
        except TypeError:
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
        except TypeError:
            self.solarElongation = None
        
        try:
            self.lunarElongation = self.getLunarElongation().degree
        except TypeError:
            self.lunarElongation = None
        super(Sighting, self).save(*args, **kwargs)

class VideoFrame(models.Model):
    class Meta:
        verbose_name                = 'meteor video frame'

    id                              = models.AutoField(
                                        primary_key         = True,
                                        verbose_name        = "ID",
                                    )
    timestamp                       = models.DateTimeField()
    sighting                        = models.ForeignKey(
                                        'meteors.Sighting',
                                        null                = True,
                                        on_delete           = models.SET_NULL,
                                    )

class Shower(core.models.NamedModel):
    class Meta:
        verbose_name                = 'meteor shower'

    
