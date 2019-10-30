import datetime
import pytz

from django.utils.dateparse import parse_date

class DateParser():
    def __init__(self, request):
        self.date       = parse_date(request.GET.get('date', datetime.date.today().isoformat()))
        if not isinstance(self.date, datetime.date):
            self.date  = datetime.date.today()
        self.midnight   = datetime.datetime.combine(self.date, datetime.time()).replace(tzinfo = pytz.UTC)

        self.timeFrom   = self.midnight + datetime.timedelta(days = -0.5)
        self.timeTo     = self.midnight + datetime.timedelta(days = 0.5)

    def context(self):
        return {
            'date':         self.date,
            'currentDate':  (datetime.datetime.now() + datetime.timedelta(days = 0.5)).date(),
            'midnight':     self.midnight,
            'timeFrom':     self.timeFrom,
            'timeTo':       self.timeTo,
        }
