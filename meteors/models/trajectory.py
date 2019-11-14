from django.db import models

    
class Trajectory(models.Model):
    class Meta:
        verbose_name = "heliocentric trajectory"

    semimajor_axis                  = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "semi-major axis",
                                    )
    eccentricity                    = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "eccentricity",
                                    )
    inclination                     = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "inclination",
                                    )
    argument_of_perihelion          = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "argument of perihelion",
                                    )
    longitude_of_ascending_node     = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "longitude of the ascending node",
                                    )

