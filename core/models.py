from django.db import models

import functools
# Create your models here.

def none_if_error(*exceptions):
    def protected(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except exceptions as e:
                print(f"Caught exception {e.__class__.__name__} ({e}) and returning None for {function}")
                return None
        return wrapper
    return protected


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
