from admin_decorators import short_description, order_field

from django.contrib import admin
from django.db import models
from django import forms

from .models import Meteor, Sighting

class MicrosecondDateTimeWidget(forms.SplitDateTimeWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.supports_microseconds = True

@admin.register(Meteor)
class MeteorAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DateTimeField: {
            'widget': MicrosecondDateTimeWidget(
                date_format = '%Y-%m-%d',
                time_format = '%H:%M:%S.%f',
            )
        },
    }
    fieldsets = (
        ('Identity',
            {
                'fields': ['timestamp'],
            }
        ),
        ('Trajectory',
            {
                'fields': (
                    ('beginningLatitude', 'beginningLongitude', 'beginningAltitude'),
                    'beginningTime',
                    ('lightmaxLatitude', 'lightmaxLongitude', 'lightmaxAltitude'),
                    'lightmaxTime',
                    ('endLatitude', 'endLongitude', 'endAltitude'),
                    'endTime',
                    ('velocityX', 'velocityY', 'velocityZ'),
                ),
            }
        ),
        ('Photometry',
            {
                'fields': ['magnitude'],
            }
        ),
    )    
    list_display = ['formatTimestamp', 'lightmaxLatitude', 'lightmaxLongitude', 'lightmaxAltitude', 'magnitude']
    save_as = True
    
    @order_field('timestamp')
    @short_description('timestamp')
    def formatTimestamp(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")

@admin.register(Sighting)
class SightingAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DateTimeField: {
            'widget': MicrosecondDateTimeWidget(
                date_format = '%Y-%m-%d',
                time_format = '%H:%M:%S.%f',
            )
        },
    }
    readonly_fields = ['solarElongation', 'lunarElongation']

    list_display = ['lightmaxTime', 'station', 'magnitude', 'lightmaxAzimuth', 'lightmaxElevation', 'meteor']
    save_as = True
