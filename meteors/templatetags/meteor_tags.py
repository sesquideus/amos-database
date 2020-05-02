import datetime
import pytz
import math
import functools

from astropy.time import Time

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def mdash(func):
    @functools.wraps(func)
    def wrapper(arg):
        if arg is None:
            return mark_safe("&mdash;")
        else:
            return func(arg)

    return wrapper


@register.filter
def previous_day(date):
    return date + datetime.timedelta(days = -1)


@register.filter
def next_day(date):
    return date + datetime.timedelta(days = 1)


@register.filter
def magnitude_colour(magnitude: float):
    white = 1 / (1 + math.exp(magnitude / 3))
    return "hsl(0, 0%, {:.0f}%)".format(white * 75 + 25)


@register.filter
@mdash
def magnitude(mag):
    return mark_safe(f"{mag:+.2f}<sup>m</sup>")


@register.filter
@mdash
def angle(ang):
    return mark_safe(f"{ang:.2f}°")


@register.filter
@mdash
def safetime(time):
    return time.strftime("%H:%M:%S.%f")


@register.filter
def nonedash(arg):
    return mark_safe("&mdash;") if arg is None else arg

@register.filter
@mdash
def solar_longitude(timestamp):
    n = Time(timestamp).jd - 2451545.0
    l = (280.460 + 0.9856474 * n) % 360
    g = math.radians(357.528 + 0.9856003 * n) % 360
    return l + 1.915 * math.sin(g) + 0.02 * math.sin(2 * g)
