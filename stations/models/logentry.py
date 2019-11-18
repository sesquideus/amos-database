import textwrap
from django.db import models


class LogEntry(models.Model):
    class Meta:
        verbose_name                = 'log entry'
        verbose_name_plural         = 'log entries'
        ordering                    = ['created']

    station                         = models.ForeignKey(
                                        'Station',
                                        null                = True,
                                        blank               = True,
                                        verbose_name        = "station",
                                        help_text           = "the station",
                                        related_name        = "log_entries",
                                        on_delete           = models.CASCADE,
                                    )
    text                            = models.TextField(
                                        help_text           = "text of the log entry",
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
            textwrap.shorten(self.text, 50, placeholder = '...'),
        )
