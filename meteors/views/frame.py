from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def frame(request, sighting, order):
    frame = Frame.objects.filter(sighting = sighting).get(order = order)
    context = {
        'frame':        frame,
    }
    return render(request, 'meteors/frame.html', context)

