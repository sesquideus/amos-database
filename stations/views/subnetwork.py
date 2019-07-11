from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from django.views.generic.detail import DetailView

from stations.models import Subnetwork

# Create your views here.

@method_decorator(login_required, name = 'dispatch')
class SingleView(DetailView):
    model           = Subnetwork
    slug_field      = 'code'
    slug_url_kwarg  = 'code'
    template_name   = 'stations/subnetwork.html'

