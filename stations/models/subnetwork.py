import pytz

from django.db import models
from django.db.models import Prefetch, Count, F
from django.urls import reverse

import core.models
from .station import Station


class SubnetworkQuerySet(models.QuerySet):
    def with_full_stations(self):
        return self.prefetch_related(
            Prefetch(
                'stations',
                queryset=Station.objects.with_last_sighting().with_last_heartbeat(),
                to_attr='stations_full',
            )
        )

    def with_count(self):
        return self.annotate(station_count=Count('stations'))


class Subnetwork(core.models.NamedModel):
    class Meta:
        verbose_name                = 'subnetwork'
        ordering                    = ['founded']

    objects                         = SubnetworkQuerySet.as_manager()

    code                            = models.CharField(
                                        max_length          = 8,
                                        unique              = True,
                                        help_text           = "a simple unique code (2-4 uppercase letters)",
                                    )
    timezone                        = models.CharField(
                                        null                = False,
                                        blank               = False,
                                        max_length          = 64,
                                        choices             = zip(pytz.common_timezones, pytz.common_timezones),
                                        help_text           = "official timezone name",
                                    )

    founded                         = models.DateField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "founding date",
                                        help_text           = "date when the subnetwork was founded",
                                    )

    def centre(self):
        stations = self.station_set.all()
        return {
            'latitude':     sum([station.latitude for station in stations]),
            'longitude':    sum([station.longitude for station in stations]),
        }

    def get_absolute_url(self):
        return reverse('subnetwork', kwargs = {'code': self.code})
