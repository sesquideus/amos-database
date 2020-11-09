import datetime
import pytz
import logging

from pprint import pprint as pp

from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from django.views.generic.detail import DetailView, BaseDetailView
from django.views.generic.list import ListView

from stations.models import Station, Subnetwork, Heartbeat
from meteors.models import Sighting
from core.views import JSONDetailView, JSONListView, LoginDetailView

log = logging.getLogger(__name__)


class SingleView(LoginDetailView):
    model           = Heartbeat
    slug_field      = 'id'
    slug_url_kwarg  = 'id'
    template_name   = 'stations/heartbeat.html'
    context_object_name = 'heartbeat'
