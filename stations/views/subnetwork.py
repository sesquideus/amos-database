import datetime
import pytz

from core.views import LoginDetailView, LoginListView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from stations.models import Subnetwork


#@method_decorator(cache_page(5), name='dispatch')
class StatusView(LoginListView):
    model               = Subnetwork
    context_object_name = 'subnetworks'
    template_name       = 'stations/status.html'

    def get_queryset(self):
        return Subnetwork.objects.with_full_stations().with_count().order_by('founded')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = datetime.datetime.now(tz=pytz.utc)
        return context


class SingleView(LoginDetailView):
    model           = Subnetwork
    slug_field      = 'code'
    slug_url_kwarg  = 'code'
    template_name   = 'stations/subnetwork.html'
