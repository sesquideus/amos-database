from admin_decorators import short_description, order_field

from django.contrib import admin
from django.db import models
from django import forms
from django.forms.widgets import NumberInput

from .models import Meteor, Sighting

class MicrosecondDateTimeWidget(forms.SplitDateTimeWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.supports_microseconds = True

class SightingInline(admin.TabularInline):
    model = Sighting

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
    inlines = [SightingInline]
    list_display = ['timestamp', 'lightmaxLatitude', 'lightmaxLongitude', 'lightmaxAltitude', 'magnitude']
    save_as = True
    
@admin.register(Sighting)
class SightingAdmin(admin.ModelAdmin):
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
                'fields': ('meteor', 'station'),            
            }
        ),
        ('Observed trajectory',
            {
                'fields': [
                    ('beginningTime', 'beginningAltitude', 'beginningAzimuth'),                    
                    ('lightmaxTime', 'lightmaxAltitude', 'lightmaxAzimuth'),                    
                    ('endTime', 'endAltitude', 'endAzimuth'),
                    'angularSpeed',
                ]
            }
        ),
        ('Photometry', 
            {
                'fields': ['magnitude', 'solarElongation', 'lunarElongation'],
            }
        ),
    )
    readonly_fields = ['solarElongation', 'lunarElongation']

    list_display = ['lightmaxTime', 'meteor', 'station', 'magnitude', 'lightmaxAzimuth', 'lightmaxAltitude']
    list_filter = ['station']
    save_as = True
