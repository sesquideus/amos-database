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
                    ('beginning_time', 'beginning_latitude', 'beginning_longitude', 'beginning_altitude'),
                    ('lightmax_time', 'lightmax_latitude', 'lightmax_longitude', 'lightmax_altitude'),
                    ('end_time', 'end_latitude', 'end_longitude', 'end_altitude'),
                    ('velocity_x', 'velocity_y', 'velocity_z'),
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
    date_hierarchy = 'lightmax_time'

    def sighting_count(self, obj):
        return obj.sightings.count()
    sighting_count.short_description = 'sighting count'

    list_display = ['name', 'timestamp', 'subnetwork', 'lightmax_time', 'lightmax_latitude', 'lightmax_longitude', 'lightmax_altitude', 'magnitude', 'sighting_count']
    save_as = True
