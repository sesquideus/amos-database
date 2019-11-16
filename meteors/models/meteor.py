import datetime
import pytz
import numpy as np

from django.db import models
from django.db.models import Prefetch, Window, F, Q, Subquery, OuterRef, Min, Max
from django.db.models.functions import Lead
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import validate_slug
from django.utils.decorators import method_decorator

from astropy.coordinates import EarthLocation
from astropy import units

from core.models import noneIfError
from meteors.models import Sighting


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


class MeteorQuerySet(models.QuerySet):
    def with_sightings(self):
        return self.prefetch_related(
            Prefetch(
                'sightings',
                queryset=Sighting.objects.with_frames().with_station().with_lightmax().order_by('timestamp'),
            )
        )

    def with_subnetwork(self):
        return self.select_related('subnetwork')

    def with_neighbours(self):
        return self.annotate(
            previous=Subquery(
                Meteor.objects.filter(
                    timestamp__lt=OuterRef('timestamp'),
                ).order_by(
                    '-timestamp'
                ).values('name')[:1]
            ),
            next=Subquery(
                Meteor.objects.filter(
                    timestamp__gt=OuterRef('timestamp'),
                ).order_by(
                    'timestamp'
                ).values('name')[:1]
            ),
         #   previous=Window(
         #       expression=Lead('name', offset=1, default=None),
         #       order_by=F('timestamp').desc(),
         #   ),
         #   next=Window(
         #       expression=Lead('name', offset=1, default=None),
         #       order_by=F('timestamp').asc(),
         #   ),
        )

    def for_night(self, date):
        midnight = datetime.datetime.combine(date, datetime.datetime.min.time()).replace(tzinfo=pytz.UTC)
        half_day = datetime.timedelta(hours=12)
        return self.filter(
            timestamp__gte=midnight - half_day,
            timestamp__lte=midnight + half_day,
        )


class Meteor(models.Model):
    class Meta:
        verbose_name                = "meteor"
        ordering                    = ['timestamp']

    objects                         = MeteorManager.from_queryset(MeteorQuerySet)()

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
                                        auto_now_add        = True,
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
    subnetwork                      = models.ForeignKey(
                                        'stations.Subnetwork',
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "subnetwork",
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

    velocity_x                      = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "geocentric velocity at infinity, x"
                                    )
    velocity_y                      = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "geocentric velocity at infinity, y"
                                    )
    velocity_z                      = models.FloatField(
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

#    @method_decorator(noneIfError(ObjectDoesNotExist))
#    def previous(self):
#        return Meteor.objects.filter(timestamp__lt = self.timestamp).latest('timestamp').name
#
#    @method_decorator(noneIfError(ObjectDoesNotExist))
#    def next(self):
#        return Meteor.objects.filter(timestamp__gt = self.timestamp).earliest('timestamp').name

    def speed(self):
        try:
            return np.sqrt(self.velocity_x**2 + self.velocity_y**2 + self.velocity_z**2)
        except TypeError:
            return None

    def save(self, *args, **kwargs):
        if self.name is None or self.name == "":
            self.name = self.lightmaxTime.strftime('%Y%m%d-%H%M%S-%f')

        super().save(*args, **kwargs)

    def json(self):
        return {
            'id':               self.id,
            'name':             self.name,
            'beginning': {
                'longitude':    self.beginningLongitude,
                'latitude':     self.beginningLatitude,
                'altitude':     self.beginningAltitude,
            },
            'lightmax': {
                'longitude':    self.lightmaxLongitude,
                'latitude':     self.lightmaxLatitude,
                'altitude':     self.lightmaxAltitude,
            },
            'end': {
                'longitude':    self.endLongitude,
                'latitude':     self.endLatitude,
                'altitude':     self.endAltitude,
            },
        }
