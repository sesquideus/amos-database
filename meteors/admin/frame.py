from django.contrib import admin
from django.db import models
from django.forms.widgets import NumberInput
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe

from meteors.models import Frame
from .widgets import MicrosecondDateTimeWidget


class FrameInline(admin.TabularInline):
    model = Frame
    show_change_link = True

    fields = ['order', 'timestamp', 'magnitude', 'altitude', 'azimuth']
    #readonly_fields = ['order', 'timestamp', 'magnitude', 'altitude', 'azimuth']
    

@admin.register(Frame)
class FrameAdmin(admin.ModelAdmin):
    def sighting_link(self, frame):
        if frame.sighting is None:
            return mark_safe("&mdash;")
        else:
            return mark_safe('<a href="{url}">{title}</a>'.format(
                url = reverse("admin:meteors_sighting_change", args = [frame.sighting.id]),
                title = frame.sighting.id,
            ))
    sighting_link.short_description = "sighting"

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
                'fields': ('sighting', 'order'),            
            }
        ),
        ('Coordinates',
            {
                'fields': [
                    ('timestamp'),
                    ('x', 'y'),
                    ('altitude', 'azimuth'),
                ]
            }
        ),
        ('Photometry',
            {
                'fields': ('magnitude',),
            }
        ),
    )

    list_display = ['__str__', 'sighting_link', 'order', 'timestamp']
    list_filter = ['sighting']
    readonly_fields = ['id']
    save_as = True
