from django.contrib import admin
from django.db import models
from django.forms.widgets import TextInput

from meteors.models import Meteor
from .sighting import SightingInline
from .snapshot import SnapshotInline
from .widgets import MicrosecondDateTimeWidget


@admin.register(Meteor)
class MeteorAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DateTimeField: {
            'widget': MicrosecondDateTimeWidget(),
        },
        models.FloatField: {
            'widget': TextInput(attrs={
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
    )
    inlines = [SightingInline, SnapshotInline]
    date_hierarchy = 'timestamp'

    def sighting_count(self, obj):
        return obj.sightings.count()
    sighting_count.short_description = 'sighting count'

    def snapshot_count(self, obj):
        return obj.snapshots.count()
    snapshot_count.short_description = 'snapshot count'

    list_display = ['name', 'timestamp', 'subnetwork', 'sighting_count', 'snapshot_count']
    save_as = True
