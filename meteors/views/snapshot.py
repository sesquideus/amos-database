import django

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from meteors.models import Snapshot


@method_decorator(login_required, name='dispatch')
class DetailView(django.views.generic.detail.DetailView):
    model           = Snapshot
    template_name   = 'meteors/snapshot.html'

    def get_object(self):
        return Snapshot.objects.filter(
            meteor__name=self.kwargs['meteor']
        ).get(
            order=self.kwargs['order']
        )
