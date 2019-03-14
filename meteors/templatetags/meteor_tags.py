import datetime
from django import template

register = template.Library()

@register.filter
def previousDay(date):
    return date + datetime.timedelta(days = -1)

@register.filter
def nextDay(date):
    return date + datetime.timedelta(days = 1)
