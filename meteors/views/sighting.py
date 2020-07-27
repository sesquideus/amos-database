import io
import datetime

import numpy as np

import django
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
from matplotlib import ticker
from matplotlib.backends.backend_agg import FigureCanvasAgg

import core.views
from core.utils import DateParser

from meteors.forms import DateForm
from meteors.models import Sighting
from stations.models import Station


class GenericListView(core.views.LoginListView):
    model = Sighting
    context_object_name = 'sightings'
    template_name = 'meteors/list-sightings.html'


class ListDateView(GenericListView):
    def get_queryset(self):
        if self.request.GET.get('date'):
            self.date = datetime.datetime.strptime(self.request.GET['date'], '%Y-%m-%d').date()
        else:
            self.date = datetime.date.today()
        return Sighting.objects.for_night(self.date).with_everything()

    def get_context_data(self):
        context = super().get_context_data()
        context.update({
            'date': self.date,
            'form': DateForm(initial={'date': self.date}),
            'navigation': django.urls.reverse('list-sightings'),
        })
        return context

    def post(self, request):
        form = DateForm(request.POST)
        if form.is_valid():
            return django.http.HttpResponseRedirect(django.urls.reverse('list-sightings') + "?date=" + form.cleaned_data['date'].strftime("%Y-%m-%d"))
        else:
            return django.http.HttpResponseBadRequest()


class ListLatestView(GenericListView):
    def get_queryset(self):
        limit = self.kwargs.get('limit', 10)
        return Sighting.objects.with_everything().order_by('-timestamp')[:limit]

    def get_context_data(self):
        context = super().get_context_data()
        context.update({
            'navigation': django.urls.reverse('list-sightings'),
        })
        return context


class ListByStationView(ListDateView):
    template_name = 'meteors/list-sightings-station.html'

    def get_queryset(self):
        return super().get_queryset().for_station(self.kwargs['station_code'])

    def get_context_data(self):
        context = super().get_context_data()
        context['station'] = Station.objects.get(code=self.kwargs['station_code'])
        return context

    def post(self, request):
        form = DateForm(request.POST)
        if form.is_valid():
            return django.http.HttpResponseRedirect(f"{django.urls.reverse('list-sightings-by-station')}?date={form.cleaned_data['datetime'].strftime('%Y-%m-%d')}")
        else:
            return django.http.HttpResponseBadRequest()


@method_decorator(login_required, name='dispatch')
class DetailView(django.views.generic.detail.DetailView):
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
            'sighting': self.object,
            #'moon':         maxLight.getMoonInfo() if maxLight else None,
            #'sun':          maxLight.getSunInfo() if maxLight else None,
            #'maxLight':     maxLight.order if maxLight else None,
        }


@method_decorator(login_required, name='dispatch')
class DetailViewExtras(DetailView):
    queryset = Sighting.objects.with_frames().with_lightmax()

    def get_object(self):
        self.sighting = super().get_object()
        self.timestamps = [frame.flight_time.total_seconds() for frame in self.sighting.frames.all()]
        self.magnitudes = [frame.magnitude for frame in self.sighting.frames.all()]
        return self.sighting


@method_decorator(login_required, name='dispatch')
class LightCurveView(DetailViewExtras):
    def render_to_response(self, context, **response_kwargs):
        fig, ax = pyplot.subplots()
        fig.tight_layout(rect=(0.06, 0.08, 1.03, 1))
        fig.set_size_inches(5.38, 1.5)
        ax.plot(self.timestamps, self.magnitudes, marker='*')
        ax.invert_yaxis()
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:+.2f}"))

        canvas = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        pyplot.close(fig)

        response = django.http.HttpResponse(buf.getvalue(), content_type='image/png')
        response['Content-Length'] = str(len(response.content))
        return response


@method_decorator(login_required, name='dispatch')
class SkyView(DetailViewExtras):
    def render_to_response(self, context, **response_kwargs):
        def size_formatter(x):
            return 20 * np.exp(-x / 2)

        figure, axes = pyplot.subplots(subplot_kw={'projection': 'polar'})
        figure.tight_layout(rect=(0.0, 0.0, 1.0, 1.0))
        figure.set_size_inches(5.38, 5.38)

        axes.tick_params(axis='x', which='major', labelsize=20)
        axes.tick_params(axis='x', which='minor', labelsize=5)
        axes.xaxis.set_ticks([0, np.pi / 2.0, np.pi, np.pi * 3 / 2.0])
        axes.xaxis.set_ticks(np.linspace(0, 2 * np.pi, 25), minor=True)
        axes.xaxis.set_ticklabels([])
        axes.yaxis.set_ticklabels([])
        axes.yaxis.set_ticks(np.linspace(0, 90, 7))
        axes.set_ylim(0, 90)
        axes.set_facecolor('black')
        axes.grid(linewidth=0.2, color='white')

        frames = self.sighting.frames.all()
        azimuths = np.radians(90 + np.array([frame.azimuth for frame in frames]))
        altitudes = np.array(90 - np.array([frame.altitude for frame in frames]))
        colours = np.array([frame.magnitude for frame in frames])
        sizes = size_formatter(colours)

        scatter = axes.scatter(azimuths, altitudes, c=colours, s=sizes, cmap='hot', alpha=1, linewidths=0)
        cb = figure.colorbar(scatter, extend='max', fraction=0.1, pad=0.06)
        cb.set_label('apparent magnitude', fontsize=16)
        cb.ax.tick_params(labelsize=15)

        canvas = FigureCanvasAgg(figure)
        buf = io.BytesIO()
        canvas.print_png(buf)
        pyplot.close(figure)

        response = django.http.HttpResponse(buf.getvalue(), content_type='image/png')
        response['Content-Length'] = str(len(response.content))

        return response
