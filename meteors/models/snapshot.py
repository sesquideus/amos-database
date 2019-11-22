import datetime
import pytz

from django.db import models


class SnapshotManager(models.Manager):
    pass 

class SnapshotQuerySet(models.QuerySet):
    def with_flight_time(self):
        return self.annotate(
            flight_time=F('timestamp') - Window( 
                expression=Min('timestamp'), 
                partition_by=F('meteor__id'), 
            )
        )


class Snapshot(models.Model):
    class Meta:
        verbose_name                = "meteor snapshot"
        ordering                    = ['meteor', 'timestamp']
        constraints                 = [
                                        models.UniqueConstraint(
                                            fields          = ['meteor', 'order'],
                                            name            = 'snapshot_ordering',
                                        )
                                    ]
        indexes                     = [
                                        models.Index(
                                            fields          = ['meteor', 'order'],
                                            name            = 'meteor_order',
                                        )
                                    ]

    objects                         = SnapshotManager.from_queryset(SnapshotQuerySet)()

    id                              = models.AutoField(
                                        primary_key         = True,
                                        verbose_name        = "ID",
                                    )
    meteor                          = models.ForeignKey(
                                        'Meteor',
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "meteor",
                                        related_name        = 'snapshots',
                                        on_delete           = models.CASCADE,
                                    )
    order                           = models.PositiveSmallIntegerField()
    timestamp                       = models.DateTimeField(
                                        verbose_name        = "timestamp",
                                    )

    latitude                        = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "latitude",
                                    )
    longitude                       = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "longitude",
                                    )
    altitude                        = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "altitude",
                                    )
    velocity_x                      = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "velocity in the x direction",
                                    )
    velocity_y                      = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "velocity in the y direction",
                                    )
    velocity_z                      = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "velocity in the z direction",
                                    )
    magnitude                       = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "absolute magnitude"
                                    )

    def earth_location(self):
        try:
            result = EarthLocation.from_geodetic(self.longitude * units.deg, self.latitude * units.deg, self.altitude * units.m)
        except TypeError:
            result = None
        return result

    def speed(self):
        try:
            return np.sqrt(self.velocity_x**2 + self.velocity_y**2 + self.velocity_z**2)
        except TypeError:
            return None

    def __str__(self):
        return f"Meteor {self.meteor}, snapshot {self.order}"
