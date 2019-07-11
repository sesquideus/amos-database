from django.db import models
from django.urls import reverse

import core.models
from .station import Station


class Subnetwork(core.models.NamedModel):
    class Meta:
        verbose_name                = 'subnetwork'
        ordering                    = ['id']

    code                            = models.CharField(
                                        max_length          = 8,
                                        unique              = True,
                                        help_text           = "a simple unique code (2-4 uppercase letters)",
                                    )

    founded                         = models.DateField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "founding date",
                                        help_text           = "date when the subnetwork was founded",
                                    )

    def count(self):
        return Station.objects.filter(subnetwork = self.id).count()
    count.short_description = 'Station count'

    def centre(self):
        stations = self.station_set.all()
        return {
            'latitude':     sum([station.latitude for station in stations]),
            'longitude':    sum([station.longitude for station in stations]),
        }

    def get_absolute_url(self):
        return reverse('subnetwork', kwargs = {'code': self.code})
