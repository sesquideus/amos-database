import textwrap
from django.conf import settings
from django.db import models


class LogEntryQuerySet(models.QuerySet):
    def for_station(self, station_code):
        return self.filter(station__code=station_code)


class LogEntry(models.Model):
    class Meta:
        verbose_name                = 'log entry'
        verbose_name_plural         = 'log entries'
        ordering                    = ['created']

    objects                         = LogEntryQuerySet.as_manager()

    station                         = models.ForeignKey(
                                        'Station',
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "station",
                                        help_text           = "the station",
                                        related_name        = "log_entries",
                                        on_delete           = models.CASCADE,
                                    )
    author                          = models.ForeignKey(
                                        settings.AUTH_USER_MODEL,
                                        null                = True,
                                        verbose_name        = "author of the entry",
                                        related_name        = "log_entries",
                                        on_delete           = models.SET_NULL,
                                    )
    text                            = models.TextField(
                                        help_text           = "text of the log entry",
                                    )
    date                            = models.DateField(
                                        null                = True,
                                        blank               = True,
                                    )
    created                         = models.DateTimeField(
                                        auto_now_add        = True,
                                    )
    updated                         = models.DateTimeField(
                                        auto_now            = True,
                                    )

    def __str__(self):
        return "[{}] {}".format(
            self.created.strftime('%Y-%m-%d %H:%M:%S'),
            textwrap.shorten(self.text, 50, placeholder='...'),
        )
