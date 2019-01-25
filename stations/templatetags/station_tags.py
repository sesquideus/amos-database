import math
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

def reduceAzimuth(azimuth: float, number: int):
    return math.floor((azimuth % 360.0) * number / 360.0 + 0.5)

@register.filter
def formatAzimuth(azimuth: float):
    return ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'][reduceAzimuth(azimuth, 16)]

@register.filter(is_safe = True)
def arrowAzimuth(azimuth: float):
    return mark_safe("&#{};".format([8593, 8599, 8594, 8600, 8595, 8601, 8592, 8598][reduceAzimuth(azimuth, 8)]))

@register.filter
def altitudeColour(altitude: float):
    if altitude < 0:
        return "hsl(240, 100%, {:.0f}%);".format(altitude * 100.0 / 180.0 + 50)
    return "hsl({:.0f}, 100%, 48%);".format(30 + altitude * 30.0 / 90.0)

@register.filter
def multiply(value: float, factor: float):
    return value * factor
