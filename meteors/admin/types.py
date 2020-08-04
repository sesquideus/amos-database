from django.db import models
from .widgets import MicrosecondDateTimeWidget


class MicrosecondMixin():
    formfield_overrides = {
        models.DateTimeField: {
            'widget': MicrosecondDateTimeWidget(
                date_format='%Y-%m-%d',
                time_format='%H:%M:%S.%f',
                attrs={'style': 'width: 100px;'},
            )
        },
    }
