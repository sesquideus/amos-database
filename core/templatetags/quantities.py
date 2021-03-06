import datetime
import django
import math
import pytz
import astropy

from astropy.time import Time
from django.utils.safestring import mark_safe

from .utilities import default_string, empty_on_error, graceful

register = django.template.Library()


@register.filter
@graceful
def latitude(value: float):
    ns = 'N' if value > 0 else 'S'
    return f"{abs(value):.6f}° {ns}"


@register.filter
@graceful
def longitude(value: float):
    ew = 'E' if value > 0 else 'W'
    return f"{abs(value):.6f}° {ew}"


@register.filter
@graceful
def altitude(value: float):
    return f"{abs(value):.0f} m"


@register.filter
@graceful
def distance(value: float):
    return f"{value:.0f} m"


@register.filter
@graceful
def temperature(value: float):
    return f"{value:.1f} °C"


@register.filter
@graceful
def pressure(value: float):
    return f"{value / 1000:.2f} kPa"


@register.filter
@graceful
def humidity(value: float):
    return f"{value:.0f} %"


@register.filter
@graceful
def speed(value: float):
    return f"{value:.0f} m/s"


@register.filter
@graceful
def magnitude(value: float):
    return mark_safe(f"{value:+.2f}<sup>m</sup>")


@register.filter
@graceful
def megabytes(value: float):
    return f"{(float(value) / 1024**2):.0f} MB"


@register.filter
@graceful
def gigabytes(value: float):
    return f"{(float(value) / 1024**3):.0f} GB"


@register.filter
@graceful
def seconds(value: float):
    return f"{value:.3f} s"


@register.filter
@graceful
def angle(value: float):
    return mark_safe(f"{value:.2f}°")


@register.filter
def boolean(value: bool, strings="yes,no"):
    true, false = strings.split(",")
    return true if value else false


@register.filter
def troolean(value, strings="yes,no,&mdash;"):
    true, false, none = strings.split(",")
    if value is None:
        return mark_safe(none)
    else:
        return mark_safe(true) if value else mark_safe(false)

@register.filter
def trivalue(value):
    if value is None:
        return mark_safe('&mdash;')
    else:
        return mark_safe(f'<span class="{"en" if value else "dis"}abled">&#1000{4 if value else 6};</span>')


@register.filter
@graceful
def solar_longitude(timestamp: datetime.datetime):
    n = Time(timestamp).jd - 2451545.0
    l = (280.460 + 0.9856474 * n) % 360
    g = math.radians(357.528 + 0.9856003 * n) % 360
    return l + 1.915 * math.sin(g) + 0.02 * math.sin(2 * g)


@register.filter
def solar_declination(timestamp: datetime.datetime):
    return astropy.coordinates.get_sun(Time(timestamp)).dec.degree


@register.filter
def since_date_time(timestamp: datetime.datetime):
    delta = (datetime.datetime.now(tz=pytz.utc) - timestamp).total_seconds()
    delta = int(math.floor(delta))
    if delta < 60:
        return f"{delta:d}s"
    if delta < 3600:
        return f"{delta // 60:d}m{delta % 60:02d}s"
    if delta < 86400:
        return f"{delta // 3600:d}h{(delta % 3600) // 60:02d}m"
    if delta < 30*36400:
        return f"{delta // 86400:d}d{(delta % 86400) // 3600:02d}h"
    return f"{delta // 86400:d}d"


@register.filter
def multiply(value: float, factor: float):
    return None if value is None else value * factor


@register.filter
def divide(value:float, factor: float):
    return None if value is None else value / factor


@register.filter
@graceful
@empty_on_error(AttributeError)
def safetime(time):
    return time.strftime("%H:%M:%S.%f")
