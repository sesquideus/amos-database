import datetime
import math
from django import template

register = template.Library()

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
