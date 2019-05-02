from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from meteors.models import Frame

@login_required
def single(request, sighting, order):
    frame = 
    context = {
        'frame': frame,
    }
    return render(request, 'meteors/frame.html', context)

@method_decorator(login_required, name = 'dispatch')
class SingleView(DetailView):
    model           = Frame
    template_name   = 'meteors/sighting.html'

    def get_object(self):
        return Frame.objects.filter(sighting = sighting).get(order = order)

    def get_context_data(self, **kwargs):
        maxLight = self.object.lightmaxFrame()
        return {
            'sighting':     self.object,
        }
