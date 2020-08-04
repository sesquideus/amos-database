import math

from django.db import models
from django.db.models import F, Q, Window, Subquery, OuterRef, Min, Max, Window
from django.db.models.functions import Lead
from django.urls import reverse
from django.utils.decorators import method_decorator

from astropy.coordinates import EarthLocation, AltAz, get_sun, get_moon
from astropy.time import Time
from astropy import units

from core.models import none_if_error


class FrameQuerySet(models.QuerySet):
    def with_flight_time(self):
        return self.annotate(
            flight_time=F('timestamp') - Window(
                expression=Min('timestamp'),
                partition_by=F('sighting__id'),
            )
        )


class Frame(models.Model):
    class Meta:
        verbose_name                = "sighting frame"
        ordering                    = ['sighting__id', 'order']
        get_latest_by               = 'timestamp'
        constraints                 = [
                                        models.UniqueConstraint(
                                            fields          = ['sighting', 'order'],
                                            name            = 'frame_ordering',
                                        )
                                    ]
        indexes                     = [
                                        models.Index(
                                            fields          = ['sighting', 'order'],
                                            name            = 'sighting_order',
                                        )
                                    ]

    objects                         = FrameQuerySet.as_manager()

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
    angular_speed                   = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "observed angular speed [°/s]",
                                    )

    solar_elongation                = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "solar elongation",
                                    )
    lunar_elongation                = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "lunar elongation",
                                    )
    def __str__(self):
        return f"Sighting {self.sighting.id}, frame {self.order}"

    def get_absolute_url(self):
        return reverse('frame', kwargs = {'sighting': self.sighting.id, 'order': self.order})

    def earthLocation(self):
        try:
            result = EarthLocation.from_geodetic(self.longitude * units.deg, self.latitude * units.deg, self.altitude * units.m)
        except TypeError:
            result = None
        return result

    @method_decorator(none_if_error(AttributeError))
    def sky_coord(self):
        return AltAz(
            alt         = self.altitude * units.degree,
            az          = self.azimuth * units.degree,
            location    = self.sighting.station.earth_location(),
            obstime     = Time(self.timestamp),
        )

    def coord_alt_az(self):
        if self.sighting is None or self.sighting.station is None:
            return None
        else:
            return AltAz(obstime = Time(self.timestamp), location = self.sighting.station.earth_location())

    @method_decorator(none_if_error(AttributeError))
    def distance(self):
        obsLoc = self.sighting.station.earth_location()
        metLoc = self.earth_location()
        return np.sqrt((obsLoc.x - metLoc.x)**2 + (obsLoc.y - metLoc.y)**2 + (obsLoc.z - metLoc.z)**2).to(units.km).round(1)

    def get_sun(self):
        if self.coord_alt_az() is None:
            return None
        else:
            return get_sun(Time(self.timestamp)).transform_to(self.coord_alt_az())

    def get_moon(self):
        if self.coord_alt_az() is None:
            return None
        else:
            return get_moon(Time(self.timestamp)).transform_to(self.coord_alt_az())

    @method_decorator(none_if_error(AttributeError, TypeError))
    def get_solar_elongation(self):
        if self.solar_elongation is None:
            return self.compute_solar_elongation()
        else:
            return self.solar_elongation

    @method_decorator(none_if_error(AttributeError, TypeError))
    def compute_solar_elongation(self):
        return self.get_sun().separation(self.sky_coord()).degree

    @method_decorator(none_if_error(AttributeError, TypeError))
    def get_lunar_elongation(self):
        if self.lunar_elongation is None:
            return self.compute_lunar_elongation()
        else:
            return self.lunar_elongation

    @method_decorator(none_if_error(AttributeError, TypeError))
    def compute_lunar_elongation(self):
        return self.get_moon().separation(self.sky_coord()).degree

    def get_sun_info(self):
        sun = self.get_sun()
        elong = self.get_solar_elongation()
        return {
            'coord': sun,
            'elong': elong,
        }

    def get_moon_info(self):
        moon = self.get_moon()
        elong = self.get_lunar_elongation()
        return {
            'coord': moon,
            'elong': elong,
        }

    @method_decorator(none_if_error(TypeError))
    def air_mass(self):
        return 1 / math.sin(math.radians(self.altitude))

    def save(self, *args, **kwargs):
        self.solar_elongation = self.get_solar_elongation()
        self.lunar_elongation = self.get_lunar_elongation()
        super().save(*args, **kwargs)
