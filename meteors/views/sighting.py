import io
import datetime

from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
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
        if self.request.GET.get('date'):
            self.date = datetime.datetime.strptime(self.request.GET['date'], '%Y-%m-%d').date()
        else:
            self.date = datetime.date.today()
        return Sighting.objects.for_night(self.date).with_everything()

    def get_context_data(self):
        context = super().get_context_data()
        context.update({
            'form':         DateForm(initial={'date': self.date}),
            'navigation':   reverse('list-sightings'),
            'date':         self.date,
        })
        return context

    def post(self, request):
        form = DateForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('list-sightings') + "?date=" + form.cleaned_data['date'].strftime("%Y-%m-%d"))
        else:
            return HttpResponseBadRequest()


@method_decorator(login_required, name = 'dispatch')
class ListByStationView(ListDateView):
    template_name = 'meteors/list-sightings-station.html'

    def get_queryset(self):
        return super().get_queryset().for_station(self.kwargs['station-code'])
    
    def get_context_data(self):
        context = super().get_context_data()
        context['station'] = Station.objects.get(code = self.kwargs['station-code'])
        return context

    def post(self, request):
        form = DateForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('list-sightings-by-station') + "?date=" + form.cleaned_data['datetime'].strftime("%Y-%m-%d"))
        else:
            return HttpResponseBadRequest()


@method_decorator(login_required, name = 'dispatch')
class SingleView(DetailView):
    model           = Sighting
    queryset        = Sighting.objects.with_neighbours().with_frames().with_station().with_meteor().with_lightmax()
    slug_field      = 'id'
    slug_url_kwarg  = 'id'
    template_name   = 'meteors/sighting.html'

    def get_object(self):
        sighting = super().get_object()
        frames = sighting.frames
        if frames.count() == 0:
            sighting.frame_first, sighting.frame_lightmax, sighting.frame_last = None, None, None
        else:
            sighting.frame_first, sighting.frame_lightmax, sighting.frame_last = sighting.frames.order_by('timestamp')[0], sighting.frames.order_by('-timestamp')[0], sighting.frames.order_by('magnitude')[0]
        return sighting

    def get_context_data(self, **kwargs):
        return {
            'sighting':     self.object,
            #'moon':         maxLight.getMoonInfo() if maxLight else None,
            #'sun':          maxLight.getSunInfo() if maxLight else None,
            #'maxLight':     maxLight.order if maxLight else None,
        }


@login_required
class LightCurveView(DetailView):
    model = Sighting
    slug_field = 'id'
    slug_url_kwargs = 'id'
    queryset = Sighting.objects.with_frames().with_lightmax()

def light_curve(request, id):
    sighting = Sighting.objects.with_frames().get(id=id)
    timestamps = [frame.flight_time.total_seconds() for frame in sighting.frames.all()]
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
