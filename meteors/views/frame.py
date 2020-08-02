import django

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from meteors.models import Frame


@method_decorator(login_required, name='dispatch')
class DetailView(django.views.generic.detail.DetailView):
    model           = Frame
    template_name   = 'meteors/frame.html'

    def get_object(self):
        return Frame.objects.filter(
            sighting=self.kwargs['sighting']
        ).get(
            order=self.kwargs['order']
        )
