from django.contrib import admin
from django.db import models
from django.forms.widgets import TextInput

from meteors.models import Snapshot
from .widgets import MicrosecondDateTimeWidget


class SnapshotInline(admin.TabularInline):
    model = Snapshot
    show_change_link = True
    extra = 0

    fields = ['order', 'timestamp', 'latitude', 'longitude', 'altitude', 'magnitude']

    formfield_overrides = {
        models.DateTimeField: {
            'widget': MicrosecondDateTimeWidget(),
        },
    }


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
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
                    ('meteor', 'order'),
                    ('timestamp',),
                ),
            },
        ),
        ('Position',
            {
                'fields': (
                    ('latitude', 'longitude', 'altitude'),
                    ('velocity_x', 'velocity_y', 'velocity_z'),
                    ('magnitude',),
                ),
            },
        ),
    )
    date_hierarchy = 'timestamp'

    list_display = ['order', 'timestamp', 'meteor']
    save_as = True
