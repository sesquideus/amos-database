from django.contrib import admin
from django.db import models
from django.forms.widgets import NumberInput
from django.urls import reverse
from django.utils.safestring import mark_safe

from meteors.models import Sighting
from .frame import FrameInline
from .widgets import MicrosecondDateTimeWidget


class SightingInline(admin.TabularInline):
    model = Sighting
    show_change_link = True

    fields = ['station', 'angularSpeed', 'magnitude', 'lightmaxAltitude', 'lightmaxAzimuth']
    readonly_fields = ['station', 'angularSpeed', 'magnitude', 'lightmaxAltitude', 'lightmaxAzimuth', 'distance', 'arcLength']

    
@admin.register(Sighting)
class SightingAdmin(admin.ModelAdmin):
    def meteorLink(self, sighting):
        if sighting.meteor is None:
            return mark_safe("&mdash;")
        else:
            return mark_safe('<a href="{url}">{title}</a>'.format(
                url = reverse("admin:meteors_meteor_change", args = [sighting.meteor.id]),
                title = sighting.meteor.name,
            ))
    meteorLink.short_description = "meteor"

    def stationLink(self, sighting):
        if sighting.station is None:
            return mark_safe("&mdash;")
        else:
            return mark_safe('<a href="{url}">{title}</a>'.format(
                url = reverse("admin:stations_station_change", args = [sighting.station.id]),
                title = sighting.station.name,
            ))
    stationLink.short_description = "station"

    formfield_overrides = {
        models.DateTimeField: {
            'widget': MicrosecondDateTimeWidget(
                date_format = '%Y-%m-%d',
                time_format = '%H:%M:%S.%f',
            )
        },
        models.FloatField: {
            'widget': NumberInput(attrs = {
                'size': 10,
            })
        }
    }
    fieldsets = (
        ('Identity',
            {
                'fields': ('meteor', 'station', 'timestamp'),            
            }
        ),
        ('Photometry', 
            {
                'fields': [
                    ('magnitude', 'angularSpeed'),
                    ('solarElongation', 'lunarElongation'),
                ],
            }
        ),
        ('Images',
            {
                'fields': ['composite'],
            }
        ),
    )
    readonly_fields = ['solarElongation', 'lunarElongation']

    list_display = ['timestamp', 'meteorLink', 'stationLink', 'magnitude', 'frameCount', 'lightmaxAzimuth', 'lightmaxAltitude']
    list_filter = ['station']
    date_hierarchy = 'timestamp'
    save_as = True
    inlines = [FrameInline]
