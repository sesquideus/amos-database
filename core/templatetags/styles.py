import django
import datetime


register = django.template.Library()


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
def previous_day(date):
    return date + datetime.timedelta(days=-1)


@register.filter
def next_day(date):
    return date + datetime.timedelta(days=1)


@register.filter
def magnitude_colour(magnitude: float):
    white = 1 / (1 + math.exp(magnitude / 3))
    return "hsl(0, 0%, {:.0f}%)".format(white * 75 + 25)
