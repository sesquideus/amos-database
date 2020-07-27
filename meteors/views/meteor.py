import datetime

import django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.views import JSONDetailView, JSONListView

from meteors.models import Meteor, Sighting
from meteors.forms import DateForm

from stations.models import Station, Subnetwork


class GenericListView(LoginRequiredMixin, django.views.generic.list.ListView):
    model = Meteor
    context_object_name = 'meteors'
    template_name = 'meteors/list-meteors.html'
    queryset = Meteor.objects.with_everything()


class ListDateView(GenericListView):
    def get_queryset(self):
        if self.request.GET.get('date'):
            self.date = datetime.datetime.strptime(self.request.GET['date'], '%Y-%m-%d').date()
        else:
            self.date = datetime.date.today()
        return self.queryset.for_night(self.date)

    def get_context_data(self):
        context = super().get_context_data()
        context.update({
            'date': self.date,
            'form': DateForm(initial={'date': self.date}),
            'navigation': django.urls.reverse('list-meteors'),
        })
#        context.update(self.time.context())
        return context

    def post(self, request):
        form = DateForm(request.POST)
        if form.is_valid():
            return django.http.HttpResponseRedirect(f"{django.urls.reverse('list-meteors')}?date={form.cleaned_data['date'].strftime('%Y-%m-%d')}")
        else:
            return django.http.HttpResponseBadRequest()


class ListLatestView(GenericListView):
    def get_queryset(self):
        limit = self.kwargs.get('limit', 10)
        return Meteor.objects.with_everything().order_by('-timestamp')[:limit]


@method_decorator(login_required, name='dispatch')
class DetailView(django.views.generic.detail.DetailView):
    model           = Meteor
    slug_field      = 'name'
    slug_url_kwarg  = 'name'
    template_name   = 'meteors/meteor.html'

    def get_object(self):
        return Meteor.objects.with_everything().get(name=self.kwargs.get('name'))


@method_decorator(login_required, name='dispatch')
class DetailViewJSON(JSONDetailView):
    model           = Meteor
    slug_field      = 'name'
    slug_url_kwarg  = 'name'



@method_decorator(csrf_exempt, name='dispatch')
class APIView(View):
    def get(self, request):
        return django.http.HttpResponse('result')

    def post(self, request):
        print(f"{'*' * 20} Incoming meteor {'*' * 20}")
        #pp(request.POST)
        #pp(request.FILES)


@login_required
def singleKML(request, name):
    context = {
        'meteor': Meteor.objects.get(name=name)
    }
    return render(request, 'meteors/meteor.kml', context, content_type='application/vnd.google-earth.kml+xml')


@login_required
def singleJSON(request, name):
    meteor = Meteor.objects.get(name=name)
    data = django.core.serializers.serialize('json', [meteor])
    return django.http.JsonResponse(data, safe=False)





@login_required
def listJSON(request):
    meteors = {}
    for meteor in Meteor.objects.all():
        meteors[meteor.id] = meteor.as_dict()

    return django.http.JsonResponse(meteors)

