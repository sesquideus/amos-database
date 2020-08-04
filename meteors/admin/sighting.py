import django

from django.contrib import admin
from django.db import models
from django.forms.widgets import NumberInput
from django.utils.safestring import mark_safe

from meteors.models import Sighting
from .frame import FrameInline
from .widgets import MicrosecondDateTimeWidget


class SightingInline(admin.TabularInline):
    model = Sighting
    show_change_link = True
    extra = 0

    fields = ['station', 'timestamp', 'composite', 'altitude', 'azimuth', 'magnitude']
    readonly_fields = ['station', 'altitude', 'azimuth', 'magnitude']

    formfield_overrides = {
        models.DateTimeField: {
            'widget': MicrosecondDateTimeWidget(),
        },
    }

    def get_queryset(self, request):
        return super().get_queryset(request).with_lightmax()

    def altitude(self, obj):
        return obj.altitude
    altitude.short_description = "altitude"

    def azimuth(self, obj):
        return obj.azimuth
    azimuth.short_description = "azimuth"

    def magnitude(self, obj):
        return obj.magnitude
    magnitude.short_description = "magnitude"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Sighting)
class SightingAdmin(admin.ModelAdmin):
    def meteor_link(self, sighting):
        if sighting.meteor is None:
            return mark_safe("&mdash;")
        else:
            return mark_safe('<a href="{url}">{title}</a>'.format(
                url=django.urls.reverse("admin:meteors_meteor_change", args=[sighting.meteor.id]),
                title=sighting.meteor.name,
            ))
    meteor_link.short_description = "meteor"

    def station_link(self, sighting):
        if sighting.station is None:
            return mark_safe("&mdash;")
        else:
            return mark_safe('<a href="{url}">{title}</a>'.format(
                url=django.urls.reverse("admin:stations_station_change", args=[sighting.station.id]),
                title=sighting.station.name,
            ))
    station_link.short_description = "station"

    formfield_overrides = {
        models.DateTimeField: {
            'widget': MicrosecondDateTimeWidget(),
        },
        models.FloatField: {
            'widget': NumberInput(attrs={
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
        ('Images',
            {
                'fields': ['composite'],
            }
        ),
    )
#    readonly_fields = ['lightmaxMagnitude']

    list_display = ['timestamp', 'meteor_link', 'station_link']
    list_filter = ['station']
    date_hierarchy = 'timestamp'
    save_as = True
    inlines = [FrameInline]
