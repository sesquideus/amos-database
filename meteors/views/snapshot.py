import django

from meteors.models import Snapshot


class DetailView(django.contrib.auth.mixins.LoginRequiredMixin, django.views.generic.detail.DetailView):
    model           = Snapshot
    template_name   = 'meteors/snapshot/main.html'

    def get_object(self):
        return Snapshot.objects.filter(
            meteor__name=self.kwargs['meteor']
        ).get(
            order=self.kwargs['order']
        )
