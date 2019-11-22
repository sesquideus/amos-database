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

    def with_snapshots(self):
        return self.prefetch_related(
            Prefetch(
                'snapshots',
                queryset=Snapshot.objects.all(),
            )
        )

    def with_subnetwork(self):
        return self.select_related('subnetwork')

    def with_neighbours(self):
        return self.annotate(
         #   previous=Subquery(
         #       Meteor.objects.filter(
         #           timestamp__lt=OuterRef('timestamp'),
         #       ).order_by(
         #           '-timestamp'
         #       ).values('name')[:1]
         #   ),
         #   next=Subquery(
         #       Meteor.objects.filter(
         #           timestamp__gt=OuterRef('timestamp'),
         #       ).order_by(
         #           'timestamp'
         #       ).values('name')[:1]
         #   ),
            previous=Window(
                expression=Lead('name', offset=1, default=None),
                order_by=F('timestamp').desc(),
            ),
            next=Window(
                expression=Lead('name', offset=1, default=None),
                order_by=F('timestamp').asc(),
            ),
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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('meteor', kwargs={'name': self.name})

    def save(self, *args, **kwargs):
        if self.name is None or self.name == "":
            self.name = self.lightmax_time.strftime('%Y%m%d-%H%M%S-%f')

        super().save(*args, **kwargs)
