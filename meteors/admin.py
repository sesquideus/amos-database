from django.contrib import admin
from django.db import models
from django import forms
from .models import Meteor, Sighting

@admin.register(Meteor)
class MeteorAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DateTimeField: {
            'widget': forms.SplitDateTimeWidget(
                date_format='%Y-%m-%d',
                time_format='%H:%M:%S.%f'
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
                    'endTime'),
            }
        ),
        ('Photometry',
            {
                'fields': ['magnitude'],
            }
        ),
    )    
    list_display = ['formatTimestamp', 'lightmaxLatitude', 'lightmaxLongitude', 'lightmaxAltitude', 'magnitude']
    
    def formatTimestamp(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
    formatTimestamp.admin_order_field  = 'timestamp'
    formatTimestamp.short_description = 'Timestamp'

@admin.register(Sighting)
class SightingAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DateTimeField: {'widget': forms.SplitDateTimeWidget(date_format='%Y-%m-%d', time_format='%H:%M:%S.%f')},
    }
    readonly_fields = ['solarElongation', 'lunarElongation']

    list_display = ['formatTimestamp', 'location', 'magnitude', 'lightmaxAzimuth', 'lightmaxElevation', 'meteor']

    def formatTimestamp(self, obj):
        return obj.lightmaxTime.strftime("%Y-%m-%d %H:%M:%S.%f")
    formatTimestamp.admin_order_field  = 'lightmaxTime'
    formatTimestamp.short_description = 'Timestamp of maximum brightness'
