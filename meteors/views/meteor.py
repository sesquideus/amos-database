import datetime

import django
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.views import JSONDetailView

from meteors.models import Meteor
from meteors.forms import DateForm

from stations.models import Subnetwork


class GenericListView(django.contrib.auth.mixins.LoginRequiredMixin, django.views.generic.list.ListView):
    model = Meteor
    context_object_name = 'meteors'
    template_name = 'meteors/list-meteors.html'
    queryset = Meteor.objects.with_everything()

    def get_context_data(self):
        context = super().get_context_data()
        context.update({
            'subnetworks': Subnetwork.objects.with_stations(),
        })
        return context


class GenericDetailView(django.contrib.auth.mixins.LoginRequiredMixin, django.views.generic.detail.DetailView):
    model = Meteor
    slug_field = 'name'
    slug_url_kwarg = 'name'
    template_name = 'meteors/meteor/main.html'
    queryset = Meteor.objects.with_everything()


class ListDateView(GenericListView):
    def get_queryset(self):
        if self.request.GET.get('date'):
            self.date = datetime.datetime.strptime(self.request.GET['date'], '%Y-%m-%d').date()
        else:
            self.date = datetime.date.today()
        return self.queryset.for_date(self.date)

    def get_context_data(self):
        context = super().get_context_data()
        context.update({
            'date': self.date,
            'form': DateForm(initial={'date': self.date}),
            'navigation': django.urls.reverse('list-meteors'),
        })
        return context

    def post(self, request):
        form = DateForm(request.POST)
        if form.is_valid():
            url = django.urls.reverse('list-meteors')
            date = form.cleaned_data['date'].strftime('%Y-%m-%d')
            return django.http.HttpResponseRedirect(f"{url}?date={date}")
        else:
            return django.http.HttpResponseBadRequest()


class ListLatestView(GenericListView):
    def get_queryset(self):
        limit = self.kwargs.get('limit', 10)
        return Meteor.objects.with_everything().order_by('-timestamp')[:limit]


class ListBySubnetworkView(ListDateView):
    template_name = 'meteors/list-meteors-subnetwork.html'

    def get_queryset(self):
        if self.request.GET.get('date'):
            self.date = datetime.datetime.strptime(self.request.GET['date'], '%Y-%m-%d').date()
        else:
            self.date = datetime.date.today()
        return self.queryset.for_date(self.date)

    def get_context_data(self):
        context = super().get_context_data()
        context.update({
            'date': self.date,
            'form': DateForm(initial={'date': self.date}),
            'subnetwork': Subnetwork.objects.get(code=self.kwargs['subnetwork_code']),
            'navigation': django.urls.reverse('list-meteors'),
        })
        return context

    def post(self, request, subnetwork_code):
        form = DateForm(request.POST)
        if form.is_valid():
            url = django.urls.reverse('list-meteors-by-subnetwork', kwargs={'subnetwork_code': subnetwork_code})
            date = form.cleaned_data['date'].strftime('%Y-%m-%d')
            return django.http.HttpResponseRedirect(f"{url}?date={date}")
        else:
            return django.http.HttpResponseBadRequest()


class DetailView(GenericDetailView):
    pass


@method_decorator(login_required, name='dispatch')
class DetailViewJSON(JSONDetailView):
    model           = Meteor
    slug_field      = 'name'
    slug_url_kwarg  = 'name'



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

