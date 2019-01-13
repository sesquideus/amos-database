from django.db import models
from django.db.models import Max, Min
from django.contrib import admin

from astropy.coordinates import EarthLocation, SkyCoord, AltAz, get_sun, get_moon
from astropy.time import Time
from astropy import units

import core.models

import math
import numpy as np

class Meteor(models.Model):
    class Meta:
        verbose_name                = "meteor"
        ordering                    = ['timestamp']
        
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
                                        verbose_name        = "latitude of point of maximum brightness",
                                    )
    lightmaxLongitude               = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "longitude of point of maximum brightness",
                                    )
    lightmaxAltitude                = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "altitude of point of maximum brightness",
                                    )   
    lightmaxTime                    = models.DateTimeField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "timestamp of point of maximum brightness",
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
            time = self.timestamp.strftime("%Y%m%d-%H%M%S"),
        )

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
                                        verbose_name        = "absolute magnitude",
                                    )
    
    beginningElevation              = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                    )
    beginningAzimuth                = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                    )
    beginningTime                   = models.DateTimeField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "time of beginning",
                                    )

    lightmaxElevation               = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "elevation of point of maximum brightness",
                                    )
    lightmaxAzimuth                 = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "azimuth of point of maximum brightness",
                                    )
    lightmaxTime                    = models.DateTimeField(
                                        null                = True,
                                        blank               = True,
                                    )

    endElevation                    = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                    )
    endAzimuth                      = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                    )
    endTime                         = models.DateTimeField(
                                        null                = True,
                                        blank               = True,
                                    )
                                        

    angularSpeed                    = models.FloatField(
                                        null                = True,
                                        blank               = True,
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
                                        verbose_name        = "observer location",
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

    def colour(self):
        ex = int((self.magnitude - 5) * -30)
        return '#{0:02X}{0:02X}{0:02X}'.format(max(64, min(ex, 255)))

    def colourText(self):
        ex = int((self.magnitude - 5) * 30)
        return '#{0:02X}{0:02X}{0:02X}'.format(min(64 + ex, 255))

    def __str__(self):
        return '{time} at ({az:.1f}°, {elev:.1f}°)'.format(
            time = self.lightmaxTime.strftime("%Y-%m-%d %H:%M:%S.%f"),
            az = self.lightmaxAzimuth,
            elev = self.lightmaxElevation,
        )

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
        return AltAz(alt = self.lightmaxElevation * units.degree, az = self.lightmaxAzimuth * units.degree, location = self.station.earthLocation(), obstime = Time(self.lightmaxTime))

    def arcLength(self):
        try:
            phi1 = math.radians(self.beginningElevation)
            phi2 = math.radians(self.endElevation)
            lambda1 = math.radians(self.beginningAzimuth)
            lambda2 = math.radians(self.endAzimuth)
            return math.degrees(math.acos(math.sin(phi1) * math.sin(phi2) + math.cos(phi1) * math.cos(phi2) * math.cos(lambda1 - lambda2)))
        except TypeError as e:
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

    def getSolarElongation(self):
        loc = AltAz(obstime = Time(self.lightmaxTime), location = self.station.earthLocation())
        sun = get_sun(Time(self.lightmaxTime)).transform_to(loc)
        return sun.separation(self.skyCoord())
    
    def getLunarElongation(self):
        loc = AltAz(obstime = Time(self.lightmaxTime), location = self.station.earthLocation())
        moon = get_moon(Time(self.lightmaxTime)).transform_to(loc)
        return moon.separation(self.skyCoord())

    def save(self, *args, **kwargs):
        self.solarElongation = self.getSolarElongation().degree
        self.lunarElongation = self.getLunarElongation().degree
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

    
