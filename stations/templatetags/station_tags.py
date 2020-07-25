import math
import pytz
import datetime
from django import template
from django.utils.safestring import mark_safe

from meteors.templatetags.meteor_tags import mdash

register = template.Library()

def reduce_azimuth(azimuth: float, number: int):
    return math.floor((azimuth % 360.0) * number / 360.0 + 0.5)


@register.filter
def format_azimuth(azimuth: float):
    return ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'][reduceAzimuth(azimuth, 16)]


@register.filter
def altitude_colour_front(altitude: float):
    return 'white' if altitude < 0 else 'black'


@register.filter
def altitude_colour_back(altitude: float):
    if altitude < 0:
        return f"hsl(240, 50%, {altitude * 5.0 / 9.0 + 50:.0f}%);"
    if altitude < 30:
        return f"hsl({30 + altitude:.0f}, 100%, 70%);"
    return f"hsl(60, 100%, {70 + 20 * (altitude - 30) / 60}%);" 


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
def altitude(value: float):
    return f"{abs(value):.0f} m"


@register.filter
@mdash
def distance(value: float):
    return f"{value:.0f}"


@register.filter
@mdash
def angle(value: float):
    return f"{value:.2f}°"


@register.filter
@mdash
def temperature(value: float):
    return f"{value:.1f} °C"


@register.filter
@mdash
def pressure(value: float):
    return f"{value / 1000:.2f} kPa"


@register.filter
@mdash
def humidity(value: float):
    return f"{value:.0f} %"



@register.filter
def since_date_time(timestamp):
    delta = (datetime.datetime.now(tz = pytz.utc) - timestamp).total_seconds()
    if delta < 60:
        return f"{delta:.0f}s"
    if delta < 3600:
        return f"{delta / 60:.0f}m{delta % 60:02.0f}s"
    if delta < 86400:
        return f"{delta / 3600:.0f}h{delta % 3600 / 60:02.0f}m"
    if delta < 30*36400:
        return f"{delta / 86400:.0f}d{delta % 86400 / 3600:02.0f}h"
    return f"{delta / 86400:.0f}d"
