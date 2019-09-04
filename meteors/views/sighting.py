import io
import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from matplotlib import pyplot
from matplotlib import ticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from core.utils import DateParser

from meteors.forms import DateForm
from meteors.models import Sighting
from stations.models import Station


@method_decorator(login_required, name = 'dispatch')
class ListDateView(ListView):
    template_name = 'meteors/list-sightings.html'
    context_object_name = 'sightings'
    model = Sighting

    def get_queryset(self):
        self.time = DateParser(self.request)  
        return Sighting.objects.filter(timestamp__gte = self.time.timeFrom, timestamp__lte = self.time.timeTo)

    def get_context_data(self):
        context = super().get_context_data()
        context.update({
            'form':         DateForm(initial = {'datetime': self.time.midnight}),
            'navigation':   reverse('listSightings')
        })
        context.update(self.time.context())
        return context

    def post(self, request):
        form = DateForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('listSightings') + "?date=" + form.cleaned_data['datetime'].strftime("%Y-%m-%d"))
        else:
            return HttpResponseBadRequest()


@method_decorator(login_required, name = 'dispatch')
class ListByStationView(ListDateView):
    template_name = 'meteors/list-sightings-station.html'

    def get_queryset(self):
        return super().get_queryset().filter(station__code = self.kwargs['stationCode'])
    
    def get_context_data(self):
        context = super().get_context_data()
        context['station'] = Station.objects.get(code = self.kwargs['stationCode'])
        return context

    def post(self, request):
        form = DateForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('listSightingsByStation') + "?date=" + form.cleaned_data['datetime'].strftime("%Y-%m-%d"))
        else:
            return HttpResponseBadRequest()


@method_decorator(login_required, name = 'dispatch')
class SingleView(DetailView):
    model           = Sighting
    slug_field      = 'id'
    slug_url_kwarg  = 'id'
    template_name   = 'meteors/sighting.html'

    def get_context_data(self, **kwargs):
        maxLight = self.object.lightmaxFrame()
        return {
            'sighting':     self.object,
            'moon':         maxLight.getMoonInfo() if maxLight else None,
            'sun':          maxLight.getSunInfo() if maxLight else None,
            'maxLight':     maxLight.order if maxLight else None,
        }


@login_required
def lightCurve(request, id):
    sighting = Sighting.objects.get(id = id)
    timestamps = [frame.flightTime() for frame in sighting.frames.all()]
    magnitudes = [frame.magnitude for frame in sighting.frames.all()]

    fig, ax = pyplot.subplots()
    fig.tight_layout(rect = (0.06, 0.08, 1.03, 1))
    fig.set_size_inches(5.38, 1.5)
    ax.plot(timestamps, magnitudes, marker = '*')
    ax.invert_yaxis()
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:+.2f}"))
    canvas = FigureCanvasAgg(fig)
    buf = io.BytesIO()
    
    canvas.print_png(buf)
    response = HttpResponse(buf.getvalue(), content_type = 'image/png')
    response['Content-Length'] = str(len(response.content))
    return response
