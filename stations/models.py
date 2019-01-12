from astropy.coordinates import EarthLocation
from django.db import models

class Country(models.Model):
    class Meta:
        verbose_name                = 'country'
        verbose_name_plural         = 'countries'

    id                              = models.AutoField(
                                        primary_key         = True,
                                        verbose_name        = "ID",
                                    )
    name                            = models.CharField(
                                        max_length = 64,
                                        unique = True,
                                    )

    def __str__(self):
        return self.name

class Subnetwork(models.Model):
    class Meta:
        verbose_name                = 'subnetwork'

    id                              = models.AutoField(
                                        primary_key         = True,
                                        verbose_name        = "ID",
                                    )
    name                            = models.CharField(
                                        max_length          = 16,
                                        unique              = True,
                                    )

    def __str__(self):
        return self.name

    def count(self):
        return Station.objects.filter(subnetwork = self.id).count()
    count.short_description = 'Station count'

class Station(models.Model):
    class Meta:
        verbose_name                = 'station'

    id                              = models.AutoField(
                                        primary_key         = True,
                                        verbose_name        = "ID",
                                    )

    code                            = models.CharField(
                                        max_length          = 8,
                                        unique              = True,
                                        help_text           = "A simple code, composed of 2-4 letters",
                                    )

    name                            = models.CharField(
                                        max_length          = 64,
                                        unique              = True,
                                        help_text           = "Printable, user-friendly name of the station",
                                    )

    subnetwork                      = models.ForeignKey(
                                        'Subnetwork',
                                        null                = True,
                                        blank               = True,
                                        on_delete           = models.CASCADE, 
                                    )
    country                         = models.ForeignKey(
                                        'Country',
                                        on_delete           = models.CASCADE,
                                    )

    latitude                        = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "latitude",
                                        help_text           = "[-90°, 90°], north positive",
                                    )
    longitude                       = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "longitude",
                                        help_text           = "[-180°, 180°], east positive",
                                    )
    altitude                        = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "altitude",
                                        help_text           = "metres above mean sea level",
                                    )   

    def __str__(self):
        return "{name} ({subnetwork})".format(
            name        = self.name,
            subnetwork  = self.subnetwork,
        )

    def earthLocation(self):
        return EarthLocation.from_geodetic(self.longitude, self.latitude, self.altitude)
    
    def register(self, meteor):
        return meteor.earthLocation() - self.earthLocation()

class Observer(models.Model):
    class Meta:
        verbose_name                = 'observer'
   
    id                              = models.AutoField(
                                        primary_key         = True,
                                        verbose_name        = "ID",
                                    )
    
    name                            = models.CharField(
                                        max_length          = 64,
                                    )

    def __str__(self):
        return self.name
   
