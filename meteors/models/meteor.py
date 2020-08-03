import datetime
import math
import pytz
import numpy as np

from django.db import models
from django.db.models import Prefetch, Window, F, Q, Subquery, OuterRef, Min, Max
from django.db.models.functions import Lead, Sqrt
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import validate_slug
from django.utils.decorators import method_decorator

from astropy.coordinates import EarthLocation
from astropy import units

from core.models import none_if_error
from meteors.models import Sighting, Snapshot


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

    def with_lightmax(self):
        snapshots = Snapshot.objects.filter(meteor=OuterRef('id')).with_speed()
        by_magnitude = snapshots.order_by('magnitude')
        by_timestamp = snapshots.order_by('timestamp')

        return self.annotate(
            magnitude=Subquery(by_magnitude.values('magnitude')[:1]),
            latitude=Subquery(by_magnitude.values('latitude')[:1]),
            longitude=Subquery(by_magnitude.values('longitude')[:1]),
            altitude=Subquery(by_magnitude.values('altitude')[:1]),
            speed=Subquery(by_timestamp.values('speed')[:1]),
        )

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
            timestamp__gte=(midnight - half_day),
            timestamp__lte=(midnight + half_day),
        )

    def for_subnetwork(self, subnetwork_code):
        return self.filter(subnetwork__code=subnetwork_code)

    def with_everything(self):
        return self.with_sightings().with_subnetwork().with_snapshots().with_lightmax()


class Meteor(models.Model):
    class Meta:
        verbose_name                = "meteor"
        ordering                    = ['timestamp']

    objects                         = MeteorQuerySet.as_manager()

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

    def as_dict(self):
        return {
            'id': self.id,
        }
