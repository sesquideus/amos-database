from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Profile(models.Model):
    user                    = models.OneToOneField(
                                User,
                                on_delete = models.CASCADE,
                            )
    latitude                = models.FloatField(
                                blank = True,
                                null = True,
                            )
    longitude               = models.FloatField(
                                blank = True,
                                null = True,
                            )

    def format_location(self):
        try:
            return "{lat:.6f}° {ns}, {lon:.6f}° {ew}".format(
                lat = self.latitude,
                lon = self.longitude,
                ns  = 'N' if self.latitude > 0 else 'S',
                ew  = 'E' if self.longitude > 0 else 'W',
            )
        except TypeError:
            return "undefined"

    def __str__(self):
        return f"Profile for {self.user.get_full_name()}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
