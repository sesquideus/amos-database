from django.db import models
from django.db.models import UniqueConstraint, Index
from .sighting import Sighting

class Frame(models.Model):
    class Meta:
        verbose_name                = "sighting frame"
        ordering                    = ['sighting__id', 'order']
        constraints                 = [
                                        UniqueConstraint(
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
                                    )

    order                           = models.PositiveSmallIntegerField()

    timestamp                       = models.DateTimeField(
                                        null                = True,
                                        blank               = True,
                                    )
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
