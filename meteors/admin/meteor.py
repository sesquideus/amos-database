from django.contrib import admin
from django.db import models
from django.forms.widgets import TextInput

from meteors.models import Meteor
from .sighting import SightingInline
from .widgets import MicrosecondDateTimeWidget


@admin.register(Meteor)
class MeteorAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DateTimeField: {
            'widget': MicrosecondDateTimeWidget(
                date_format = '%Y-%m-%d',
                time_format = '%H:%M:%S.%f',
            )
        },
        models.FloatField: {
            'widget': TextInput(attrs = {
                'style': 'width: 80px;',
                'class': 'narrow',
            })
        }
    }
    fieldsets = (
        ('Identity',
            {
                'fields': (
                    ('name',),
                    ('subnetwork',),
                ),
            },
        ),
        ('Trajectory',
            {
                'fields': (
                    ('beginningTime', 'beginningLatitude', 'beginningLongitude', 'beginningAltitude'),
                    ('lightmaxTime', 'lightmaxLatitude', 'lightmaxLongitude', 'lightmaxAltitude'),
                    ('endTime', 'endLatitude', 'endLongitude', 'endAltitude'),
                    ('velocityX', 'velocityY', 'velocityZ'),
                ),
            },
        ),
        ('Photometry',
            {
                'fields': ('magnitude',),
            },
        ),
    )
    inlines = [SightingInline]
    date_hierarchy = 'lightmaxTime'

    def sightingCount(self, obj):
        return obj.sightings.count()
    sightingCount.short_description = 'sighting count'

    list_display = ['name', 'subnetwork', 'lightmaxTime', 'lightmaxLatitude', 'lightmaxLongitude', 'lightmaxAltitude', 'magnitude', 'sightingCount']
    save_as = True
