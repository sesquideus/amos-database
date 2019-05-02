from django.db import models
    
class Trajectory(models.Model):
    class Meta:
        verbose_name = "heliocentric trajectory"

    semiMajorAxis                   = models.FloatField(
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
    argumentOfPerihelion            = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "argument of perihelion",
                                    )
    meanAnomaly                     = models.FloatField(
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "mean anomaly",
                                    )

