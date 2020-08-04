import datetime
import django
import math
import pytz

from astropy.time import Time
from django.utils.safestring import mark_safe

from .utilities import mdash, empty_on_error

register = django.template.Library()


@register.filter
@mdash
@empty_on_error(ValueError, TypeError)
def latitude(value: float):
    ns = 'N' if value > 0 else 'S'
    return f"{abs(value):.6f}° {ns}"


@register.filter
@mdash
@empty_on_error(ValueError, TypeError)
def longitude(value: float):
    ew = 'E' if value > 0 else 'W'
    return f"{abs(value):.6f}° {ew}"


@register.filter
@mdash
@empty_on_error(ValueError, TypeError)
def altitude(value: float):
    return f"{abs(value):.0f} m"


@register.filter
@mdash
@empty_on_error(ValueError, TypeError)
def distance(value: float):
    return f"{value:.0f} m"


@register.filter
@mdash
@empty_on_error(ValueError, TypeError)
def temperature(value: float):
    return f"{value:.1f} °C"


@register.filter
@mdash
@empty_on_error(ValueError, TypeError)
def pressure(value: float):
    return f"{value / 1000:.2f} kPa"


@register.filter
@mdash
@empty_on_error(ValueError, TypeError)
def humidity(value: float):
    return f"{value:.0f} %"


@register.filter
@mdash
@empty_on_error(ValueError, TypeError)
def speed(value: float):
    return f"{value:.0f} m/s"


@register.filter
@mdash
@empty_on_error(ValueError, TypeError)
def magnitude(mag):
    return mark_safe(f"{mag:+.2f}<sup>m</sup>")


@register.filter
@mdash
@empty_on_error(ValueError)
def angle(ang):
    return mark_safe(f"{ang:.2f}°")


@register.filter
@mdash
def solar_longitude(timestamp):
    n = Time(timestamp).jd - 2451545.0
    l = (280.460 + 0.9856474 * n) % 360
    g = math.radians(357.528 + 0.9856003 * n) % 360
    return l + 1.915 * math.sin(g) + 0.02 * math.sin(2 * g)


@register.filter
def since_date_time(timestamp):
    delta = (datetime.datetime.now(tz=pytz.utc) - timestamp).total_seconds()
    if delta < 60:
        return f"{delta:.0f}s"
    if delta < 3600:
        return f"{delta // 60:.0f}m{delta % 60:02.0f}s"
    if delta < 86400:
        return f"{delta // 3600:.0f}h{(delta % 3600) // 60:02.0f}m"
    if delta < 30*36400:
        return f"{delta // 86400:.0f}d{(delta % 86400) // 3600:02.0f}h"
    return f"{delta // 86400:.0f}d"


@register.filter
def multiply(value: float, factor: float):
    return None if value is None else value * factor


@register.filter
@mdash
@empty_on_error(AttributeError)
def safetime(time):
    return time.strftime("%H:%M:%S.%f")
