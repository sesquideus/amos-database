from django.db import models
from django.urls import reverse
from django.core.validators import validate_slug, RegexValidator

from astropy.coordinates import EarthLocation
from astropy import units

import datetime
import pytz
import numpy as np


class MeteorManager(models.Manager):
    def createFromPost(self, **kwargs):
        meteor = self.create(
            timestamp           = kwargs.get('timestamp', None),
            beginningLatitude   = kwargs.get('beginningLatitude', None),
            beginningLongitude  = kwargs.get('beginningLongitude', None),
            beginningAltitude   = kwargs.get('beginningAltitude', None),
            beginningTime       = kwargs.get('beginningTime', None),

            lightmaxLatitude    = kwargs.get('lightmaxLatitude', None),
            lightmaxLongitude   = kwargs.get('lightmaxLongitude', None),
            lightmaxAltitude    = kwargs.get('lightmaxAltitude', None),
            lightmaxTime        = kwargs.get('lightmaxTime', None),

            endLatitude         = kwargs.get('endLatitude', None),
            endLongitude        = kwargs.get('endLongitude', None),
            endAltitude         = kwargs.get('endAltitude', None),
            endTime             = kwargs.get('endTime', None),

            velocityX           = kwargs.get('velocityX', None),
            velocityY           = kwargs.get('velocityY', None),
            velocityZ           = kwargs.get('velocityZ', None),

            magnitude           = kwargs.get('magnitude', None),
        )
        return meteor


class Meteor(models.Model):
    class Meta:
        verbose_name                = "meteor"
        ordering                    = ['lightmaxTime']

    objects                         = MeteorManager()

    id                              = models.AutoField(
                                        primary_key         = True,
                                        verbose_name        = "ID",
                                    )
    name                            = models.CharField(
                                        max_length          = 64,
                                        null                = False,
                                        blank               = False,
                                        unique              = True,
                                        verbose_name        = "name",
                                        validators          = [validate_slug],
                                    )
    timestamp                       = models.DateTimeField(
                                        verbose_name        = "timestamp",
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
                                        verbose_name        = "longitude at max light",
                                    )
    lightmaxAltitude                = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "altitude at max light",
                                    )   
    lightmaxTime                    = models.DateTimeField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "timestamp at max light",
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
        return self.name

    def get_absolute_url(self):
        return reverse('meteor', kwargs = {'name': self.name})

    def asDict(self):
        return {
            'latitude':     self.lightmaxLatitude,
            'longitude':    self.lightmaxLongitude,
            'altitude':     self.lightmaxAltitude,
            'magnitude':    self.magnitude,
        }

    def earthLocation(self):
        try:
            result = EarthLocation.from_geodetic(self.lightmaxLongitude * units.deg, self.lightmaxLatitude * units.deg, self.lightmaxAltitude * units.m)
        except TypeError:
            result = None
        return result

    def previous(self):
        try:
            result = Meteor.objects.filter(lightmaxTime__lt = self.lightmaxTime).earliest('timestamp').name
        except Meteor.DoesNotExist:
            result = Meteor.objects.order_by('timestamp').last().name
        return result

    def next(self):
        try:
            result = Meteor.objects.filter(lightmaxTime__gt = self.lightmaxTime).latest('timestamp').name
        except Meteor.DoesNotExist:
            result = Meteor.objects.order_by('timestamp').first().name
        return result

    def speed(self):
        try:
            return np.sqrt(self.velocityX**2 + self.velocityY**2 + self.velocityZ**2)
        except TypeError:
            return None

    def save(self, *args, **kwargs):
        if self.name is None or self.name == "":
            self.name = self.lightmaxTime.strftime('%Y%m%d-%H%M%S-%f')

        super().save(*args, **kwargs)

    
