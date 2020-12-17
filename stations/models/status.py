from django.db import models


class Status(models.Model):
    class Meta:
        verbose_name = "status"
        verbose_name_plural = "statuses"
        ordering = ['-timestamp']
        get_latest_by = ['timestamp']

    STATUS_OK = 'O'
    STATUS_LOST = 'L'
    STATUS_OFF = 'F'
    STATUS_DISK_FULL = 'D'

    STATUS = [
        (STATUS_OK, 'online'),              # the station is working as intended
        (STATUS_OFF, 'turned off'),         # the station has been turned off intentionally
        (STATUS_LOST, 'lost contact'),      # the station does not send any reports
        (STATUS_DISK_FULL, 'disk full'),    # the station cannot observe due to a full disk
    ]

    timestamp = models.DateTimeField(verbose_name='timestamp')
    status = models.CharField(choices=STATUS)
