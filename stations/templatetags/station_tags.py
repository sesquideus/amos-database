import math
import pytz
from django import template
from django.utils.safestring import mark_safe

from meteors.templatetags.meteor_tags import mdash

register = template.Library()

def reduceAzimuth(azimuth: float, number: int):
    return math.floor((azimuth % 360.0) * number / 360.0 + 0.5)


@register.filter
def formatAzimuth(azimuth: float):
    return ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'][reduceAzimuth(azimuth, 16)]


@register.filter
def altitudeColour(altitude: float):
    if altitude < 0:
        return "hsl(240, 100%, {:.0f}%);".format(altitude * 100.0 / 180.0 + 50)
    return "hsl({:.0f}, 100%, 48%);".format(30 + altitude * 30.0 / 90.0)


@register.filter
def multiply(value: float, factor: float):
    return None if value is None else value * factor


@register.filter
@mdash
def latitude(value: float):
    ns = 'N' if value > 0 else 'S'
    return f"{abs(value):.6f}° {ns}"


@register.filter
@mdash
def longitude(value: float):
    ew = 'E' if value > 0 else 'W'
    return f"{abs(value):.6f}° {ew}"


@register.filter
@mdash
def distance(value: float):
    return f"{value:.0f}"


@register.filter
@mdash
def angle(value: float):
    return f"{value:.2f}°"
