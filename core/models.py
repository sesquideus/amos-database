from django.db import models

# Create your models here.

class NamedModel(models.Model):
    class Meta:
        abstract                    = True

    id                              = models.AutoField(
                                        primary_key         = True,
                                        verbose_name        = "ID",
                                    )
    name                            = models.CharField(
                                        max_length          = 64,
                                        unique              = True,
                                    )
    
    def __str__(self):
        return self.name
