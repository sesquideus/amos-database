import math

from django.db import models
from django.urls import reverse


class Frame(models.Model):
    class Meta:
        verbose_name                = "sighting frame"
        ordering                    = ['sighting__id', 'order']
        constraints                 = [
                                        models.UniqueConstraint(
                                            fields          = ['sighting', 'order'],
                                            name            = 'frameOrdering',
                                        )
                                    ]
        indexes                     = [
                                        models.Index(
                                            fields          = ['sighting', 'order'],
                                            name            = 'sightingOrder',
                                        )
                                    ]

    id                              = models.AutoField(
                                        primary_key         = True,
                                        verbose_name        = "surrogate key",
                                    )
    sighting                        = models.ForeignKey(
                                        'Sighting',
                                        on_delete           = models.CASCADE,
                                        related_name        = 'frames',
                                    )
    order                           = models.PositiveSmallIntegerField()
    timestamp                       = models.DateTimeField()
    x                               = models.SmallIntegerField(
                                        null                = True,
                                        blank               = True,
                                    )
    y                               = models.SmallIntegerField(
                                        null                = True,
                                        blank               = True,
                                    )
    altitude                        = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                    )
    azimuth                         = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                    )
    magnitude                       = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                    )

    def __str__(self):
        return f"Sighting {self.sighting.id}, frame {self.order}"

    def get_absolute_url(self):
        return reverse('frame', kwargs = {'sighting': self.sighting.id, 'order': self.order})

    def previous(self):
        try:
            return Frame.objects.filter(sighting__id = self.sighting.id).filter(timestamp__lt = self.timestamp).latest('timestamp').order
        except Frame.DoesNotExist:
            return None

    def next(self):
        try:
            return Frame.objects.filter(sighting__id = self.sighting.id).filter(timestamp__gt = self.timestamp).earliest('timestamp').order
        except Frame.DoesNotExist:
            return None

    def flightTime(self):
        if self.timestamp is None or self.sighting.firstFrame().timestamp is None:
            return None

        return (self.timestamp - self.sighting.firstFrame().timestamp).total_seconds()

    def airMass(self):
        try:
            return 1 / math.sin(math.radians(self.lightmaxAltitude))
        except TypeError:
            return None
