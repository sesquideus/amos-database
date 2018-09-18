from django.contrib import admin
from django.db import models
from .models import Country, Location, Observer

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
                'fields': ('name', 'country'),
            }
        ),
        ('Geographics coordinates', {
                'fields': ('latitude', 'longitude', 'altitude'),
            }
        ),
    )
    list_display = ['name', 'country', 'latitude', 'longitude', 'altitude']

@admin.register(Observer)
class ObserverAdmin(admin.ModelAdmin):
    list_display = ['name']
