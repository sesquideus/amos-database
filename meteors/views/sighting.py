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
from stations.models import Station, Subnetwork


class GenericListView(core.views.LoginListView):
    model = Sighting
    context_object_name = 'sightings'
    template_name = 'meteors/list-sightings.html'

    def get_context_data(self):
        context = super().get_context_data()
        context.update({
            'subnetworks': Subnetwork.objects.with_stations(),
        })
        return context


class ListDateView(GenericListView):
    def get_queryset(self):
        if self.request.GET.get('date'):
            self.date = datetime.datetime.strptime(self.request.GET['date'], '%Y-%m-%d').date()
        else:
            self.date = datetime.date.today()
        return Sighting.objects.for_date(self.date).with_everything()

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
            url = django.urls.reverse('list-sightings')
            return django.http.HttpResponseRedirect(f"{url}?date={form.cleaned_data['date'].strftime('%Y-%m-%d')}")
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

    def post(self, request, station_code):
        form = DateForm(request.POST)
        if form.is_valid():
            url = django.urls.reverse('list-sightings-by-station', kwargs={'station_code': station_code})
            return django.http.HttpResponseRedirect(f"{url}?date={form.cleaned_data['date'].strftime('%Y-%m-%d')}")
        else:
            return django.http.HttpResponseBadRequest()


class DetailView(core.views.LoginDetailView):
    model           = Sighting
    queryset        = Sighting.objects.with_everything()
    slug_field      = 'id'
    slug_url_kwarg  = 'id'
    template_name   = 'meteors/sighting/main.html'

    def get_object(self):
        sighting = super().get_object()
        frames = sighting.frames

        if frames.count() == 0:
            sighting.frame_first, sighting.frame_lightmax, sighting.frame_last = \
                None, None, None
        else:
            sighting.frame_first, sighting.frame_lightmax, sighting.frame_last = \
                sighting.frames.order_by('timestamp')[0], \
                sighting.frames.order_by('-timestamp')[0], \
                sighting.frames.order_by('magnitude')[0]
        return sighting

    def get_context_data(self, **kwargs):
        try:
            previous_for_station = self.object.get_previous_by_timestamp(station__code=self.object.station.code)
        except Sighting.DoesNotExist:
            previous_for_station = None

        try:
            next_for_station = self.object.get_next_by_timestamp(station__code=self.object.station.code)
        except Sighting.DoesNotExist:
            next_for_station = None

        return {
            'sighting': self.object,
            'previous_for_station': previous_for_station,
            'next_for_station': next_for_station,
            #'moon':         maxLight.getMoonInfo() if maxLight else None,
            #'sun':          maxLight.getSunInfo() if maxLight else None,
            #'maxLight':     maxLight.order if maxLight else None,
        }


class DetailViewExtras(DetailView):
    queryset = Sighting.objects.with_frames().with_lightmax()

    def get_object(self):
        self.sighting = super().get_object()
        self.timestamps = [frame.flight_time.total_seconds() for frame in self.sighting.frames.all()]
        self.magnitudes = [frame.magnitude for frame in self.sighting.frames.all()]
        return self.sighting


class LightCurveView(DetailViewExtras):
    def render_to_response(self, context, **response_kwargs):
        fig, ax = pyplot.subplots()
        fig.tight_layout(rect=(0.06, 0.08, 1.03, 1))
        fig.set_size_inches(6.4, 1.5)
        ax.invert_yaxis()
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:+.2f}"))

        ax.grid('major', 'both', color='black', linestyle=':', linewidth=0.5, alpha=0.5)
        ax.plot(self.timestamps, self.magnitudes, marker='*')
        ax.set_xlim(xmin=0)

        return core.http.FigurePNGResponse(fig)


class SkyView(DetailViewExtras):
    def render_to_response(self, context, **response_kwargs):
        def size_formatter(x):
            return 20 * np.exp(-x / 2)

        figure, axes = pyplot.subplots(subplot_kw={'projection': 'polar'})
        figure.tight_layout(rect=(0.0, 0.0, 1.0, 1.0))
        figure.set_size_inches(6.4, 5)

        axes.tick_params(axis='x', which='major', labelsize=20)
        axes.tick_params(axis='x', which='minor', labelsize=5)
        axes.xaxis.set_ticks([0, np.pi / 2.0, np.pi, np.pi * 3 / 2.0])
        axes.xaxis.set_ticks(np.linspace(0, 2 * np.pi, 25), minor=True)
        axes.xaxis.set_ticklabels([])
        axes.yaxis.set_ticklabels([])
        axes.yaxis.set_ticks(np.linspace(0, 90, 7))
        axes.set_ylim(0, 90)
        axes.set_facecolor('black')
        axes.grid(linewidth=1, color='white')

        frames = self.sighting.frames.all()
        azimuths = np.radians(90 + np.array([frame.azimuth for frame in frames]))
        altitudes = np.array(90 - np.array([frame.altitude for frame in frames]))
        colours = np.array([frame.magnitude for frame in frames])
        sizes = size_formatter(colours)

        scatter = axes.scatter(azimuths, altitudes, c=colours, s=sizes, cmap='hot_r', alpha=1, linewidths=0)
        cb = figure.colorbar(scatter, extend='max', fraction=0.2, pad=0.05)
        scatter.set_clim(-10, 10)
        cb.set_label('apparent magnitude', fontsize=12)
        cb.ax.tick_params(labelsize=10)
        cb.ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x:+5.1f}$^\\mathrm{{m}}$"))
        cb.ax.invert_yaxis()

        return core.http.FigurePNGResponse(figure)
