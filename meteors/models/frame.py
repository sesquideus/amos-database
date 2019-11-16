import math

from django.db import models
from django.db.models import F, Q, Window, Subquery, OuterRef, Min, Max, Window
from django.db.models.functions import Lead
from django.urls import reverse
from django.utils.decorators import method_decorator

from astropy.coordinates import EarthLocation, AltAz, get_sun, get_moon
from astropy.time import Time
from astropy import units

from core.models import noneIfError


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

    def previous(self):
        try:
            return Frame.objects.filter(sighting__id = self.sighting.id).filter(timestamp__lt = self.timestamp).latest()
        except Frame.DoesNotExist:
            return None

    def next(self):
        try:
            return Frame.objects.filter(sighting__id = self.sighting.id).filter(timestamp__gt = self.timestamp).earliest()
        except Frame.DoesNotExist:
            return None

    def earthLocation(self):
        try:
            result = EarthLocation.from_geodetic(self.longitude * units.deg, self.latitude * units.deg, self.altitude * units.m)
        except TypeError:
            result = None
        return result

    @method_decorator(noneIfError(AttributeError))
    def skyCoord(self):
        return AltAz(
            alt         = self.altitude * units.degree,
            az          = self.azimuth * units.degree,
            location    = self.sighting.station.earthLocation(),
            obstime     = Time(self.timestamp),
        )

    def coordAltAz(self):
        if self.sighting is None or self.sighting.station is None:
            return None
        else:
            return AltAz(obstime = Time(self.timestamp), location = self.sighting.station.earthLocation())

    @method_decorator(noneIfError(AttributeError))
    def distance(self):
        obsLoc = self.sighting.station.earthLocation()
        metLoc = self.earthLocation()
        return np.sqrt((obsLoc.x - metLoc.x)**2 + (obsLoc.y - metLoc.y)**2 + (obsLoc.z - metLoc.z)**2).to(units.km).round(1)

    def getSun(self):
        if self.coordAltAz() is None:
            return None
        else:
            return get_sun(Time(self.timestamp)).transform_to(self.coordAltAz())

    def getMoon(self):
        if self.coordAltAz() is None:
            return None
        else:
            return get_moon(Time(self.timestamp)).transform_to(self.coordAltAz())

    @method_decorator(noneIfError(AttributeError, TypeError))
    def getSolarElongation(self):
        if self.solarElongation is None:
            return self.computeSolarElongation()
        else:
            return self.solarElongation

    @method_decorator(noneIfError(AttributeError, TypeError))
    def computeSolarElongation(self):
        return self.getSun().separation(self.skyCoord()).degree

    @method_decorator(noneIfError(AttributeError, TypeError))
    def getLunarElongation(self):
        if self.lunarElongation is None:
            return self.computeLunarElongation()
        else:
            return self.lunarElongation

    @method_decorator(noneIfError(AttributeError, TypeError))
    def computeLunarElongation(self):
        return self.getMoon().separation(self.skyCoord()).degree

    def getSunInfo(self):
        sun = self.getSun()
        elong = self.getSolarElongation()
        return {
            'coord': sun,
            'elong': elong,
        }

    def getMoonInfo(self):
        moon = self.getMoon()
        elong = self.getLunarElongation()
        return {
            'coord': moon,
            'elong': elong,
        }

    def airMass(self):
        try:
            return 1 / math.sin(math.radians(self.altitude))
        except TypeError:
            return None

    def save(self, *args, **kwargs):
        self.solarElongation = self.getSolarElongation()
        self.lunarElongation = self.getLunarElongation()
        super().save(*args, **kwargs)
