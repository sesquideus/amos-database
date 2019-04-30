import io
import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.detail import DetailView

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from core.utils import DateParser

from meteors.forms import DateForm
from meteors.models import Sighting

@method_decorator(login_required, name = 'dispatch')
class ListView(View):
    def get(self, request):
        time = DateParser(request)   
        context = {
            'sightings':    Sighting.objects.filter(timestamp__gte = time.timeFrom, timestamp__lte = time.timeTo),
            'form':         DateForm(initial = {'datetime': time.midnight}),
            'navigation':   reverse('listSightings')
        }
        context.update(time.context())
        return render(request, 'meteors/list-sightings.html', context)

    def post(self, request):
        form = DateForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('listSightings') + "?date=" + form.cleaned_data['datetime'].strftime("%Y-%m-%d"))
        else:
            return HttpResponseBadRequest()


@method_decorator(login_required, name = 'dispatch')
class ListByStationView(View):
    def get(self, request, stationCode):
        time = DateParser(request)   
        context = {
            'station':      Station.objects.get(code = stationCode),
            'form':         DateForm(initial = {'datetime': time.midnight}),
            'sightings':    Sighting.objects.filter(
                                lightmaxTime__gte = time.timeFrom,
                                lightmaxTime__lte = time.timeTo,
                                station__code = stationCode,
                            ),
        }
        context.update(time.context())
        return render(request, 'meteors/list-sightings-station.html', context)


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
            'moon':         self.object.getMoonInfo(),
            'sun':          self.object.getSunInfo(),
            'maxLight':     maxLight.order if maxLight else None,
        }


@login_required
def chart(request, id):
    sighting = Sighting.objects.get(id = id)
    timestamps = [frame.flightTime() for frame in sighting.frames.all()]
    magnitudes = [frame.magnitude for frame in sighting.frames.all()]

    fig, ax = plt.subplots()
    fig.tight_layout(rect = (0, 0.05, 1.03, 1))
    fig.set_size_inches(8, 2)
    ax.plot(timestamps, magnitudes, marker = '*')
    ax.invert_yaxis()
    canvas = FigureCanvasAgg(fig)
    buf = io.BytesIO()
    
    canvas.print_png(buf)
    response = HttpResponse(buf.getvalue(), content_type = 'image/png')
    response['Content-Length'] = str(len(response.content))
    return response
