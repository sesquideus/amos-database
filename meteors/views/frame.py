from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from meteors.models import Frame

@login_required
def single(request, sighting, order):
    frame = Frame.objects.filter(sighting = sighting).get(order = order)
    context = {
        'frame': frame,
    }
    return render(request, 'meteors/frame.html', context)

