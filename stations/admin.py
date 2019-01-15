from django.contrib import admin
from django.db import models
from .models import Country, Subnetwork, Station, LogEntry

class StationInline(admin.TabularInline):
    model = Station

class LogEntryInline(admin.TabularInline):
    model = LogEntry

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass

@admin.register(Subnetwork)
class SubnetworkAdmin(admin.ModelAdmin):
    list_display = ['name', 'count']
    inlines = [StationInline]

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Properties', {
                'fields': ('name', 'code', 'subnetwork', 'country'),
            }
        ),
        ('Geographics coordinates', {
                'fields': ('latitude', 'longitude', 'altitude'),
            }
        ),
    )
    list_display = ['name', 'country', 'latitude', 'longitude', 'altitude']
    inlines = [LogEntryInline]

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    readonly_fields = ['created', 'updated']
