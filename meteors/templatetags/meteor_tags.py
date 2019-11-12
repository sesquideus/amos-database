import datetime
import math
import functools

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
def previousDay(date):
    return date + datetime.timedelta(days = -1)


@register.filter
def nextDay(date):
    return date + datetime.timedelta(days = 1)


@register.filter
def magnitudeColour(magnitude: float):
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
def since_date_time(timestamp):
    delta = (datetime.datetime.now(tz = pytz.utc) - timestamp).total_seconds()
    if delta < 60:
        return f"{delta}s"
    if delta < 3600:
        return f"{delta / 60:02.0f}m{delta % 60:02.0f}s"
    if delta < 86400:
        return f"{delta / 3600:02.0f}h{delta % 3600 / 60:02.0f}m"



