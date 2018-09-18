from astropy.coordinates import EarthLocation
from django.db import models
from meteors.models import Meteor

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

class Location(models.Model):
    class Meta:
        verbose_name                = 'location'

    id                              = models.AutoField(
                                        primary_key         = True,
                                        verbose_name        = "ID",
                                    )

    name                            = models.CharField(
                                        max_length = 64,
                                        unique = True,
                                    )

    country                         = models.ForeignKey(
                                        'Country',
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
        return "{name} ({country})".format(
            name = self.name,
            country = self.country
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
                                        max_length = 64,
                                    )

    def __str__(self):
        return self.name
   
