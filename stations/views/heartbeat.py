import logging
import core.views

from stations.models import Heartbeat

log = logging.getLogger(__name__)


class SingleView(core.views.LoginDetailView):
    model           = Heartbeat
    slug_field      = 'id'
    slug_url_kwarg  = 'id'
    template_name   = 'stations/heartbeat.html'
    context_object_name = 'heartbeat'
