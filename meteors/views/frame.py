from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.views.generic.detail import DetailView

from meteors.models import Frame


@method_decorator(login_required, name = 'dispatch')
class SingleView(DetailView):
    model           = Frame
    template_name   = 'meteors/frame.html'

    def get_object(self):
        return Frame.objects.filter(
            sighting=self.kwargs['sighting']
        ).get(
            order=self.kwargs['order']
        )
