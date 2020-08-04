from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import Country, Subnetwork, Station, LogEntry, Heartbeat


class StationInline(admin.TabularInline):
    model = Station


class LogEntryInline(admin.TabularInline):
    model = LogEntry
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs = {
                'rows': 2,
                'cols': 50,
            }),
        },
    }


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass


@admin.register(Subnetwork)
class SubnetworkAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'founded']
    inlines = [StationInline]


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Properties', {
            'fields': ('name', 'code', 'subnetwork', 'address', 'country', 'on'),
        }),
        ('Geographics coordinates', {
            'fields': ('latitude', 'longitude', 'altitude', 'timezone'),
        }),
    )
    list_display = ['name', 'code', 'address', 'subnetwork', 'on', 'latitude', 'longitude', 'altitude', 'timezone']
    list_editable = ['on']
    list_display_links = ['name', 'subnetwork']
    inlines = [LogEntryInline]


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['created', 'author', 'text']
    readonly_fields = ['created', 'updated']


@admin.register(Heartbeat)
class HeartbeatAdmin(admin.ModelAdmin):
    list_filter = ['station', 'timestamp']
    readonly_fields = ['timestamp', 'received']
