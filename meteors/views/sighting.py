from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

@method_decorator(login_required, name = 'dispatch')
class ListSightingsView(View):
    def get(self, request):
        time = DateParser(request)   
        context = {
            'sightings':    Sighting.objects.filter(timestamp__gte = time.timeFrom, timestamp__lte = time.timeTo),
            'form':         DateForm(initial = {'datetime': time.midnight}),
            'navigation':   reverse('listSightings')
        }
        context.update(time.context())
        return render(request, 'meteors/list-sightings.html', context)

    def post(self, request):
        form = DateForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('listSightings') + "?date=" + form.cleaned_data['datetime'].strftime("%Y-%m-%d"))
        else:
            return HttpResponseBadRequest()


@login_required
def listSightingsStation(request, stationCode):
    time = DateParser(request)   
    context = {
        'station':      Station.objects.get(code = stationCode),
        'form':         DateForm(initial = {'datetime': time.midnight}),
        'sightings':    Sighting.objects.filter(
                            lightmaxTime__gte = time.timeFrom,
                            lightmaxTime__lte = time.timeTo,
                            station__code = stationCode,
                        ),
    }
    context.update(time.context())
    return render(request, 'meteors/list-sightings-station.html', context)


@login_required
def sighting(request, id):
    sighting = Sighting.objects.get(id = id)
    maxLight = sighting.lightmaxFrame()
    context = {
        'sighting':     sighting,
        'moon':         sighting.getMoonInfo(),
        'sun':          sighting.getSunInfo(),
        'maxLight':     maxLight.order if maxLight else None,
    }
    print(context)
    return render(request, 'meteors/sighting.html', context)


@login_required
def sightingChart(request, id):
    sighting = Sighting.objects.get(id = id)
    timestamps = [frame.flightTime() for frame in sighting.frames.all()]
    magnitudes = [frame.magnitude for frame in sighting.frames.all()]

    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot(timestamps, magnitudes, marker = '*')
    canvas = FigureCanvasAgg(fig)
    buf = io.BytesIO()
    
    canvas.print_png(buf)
    response = HttpResponse(buf.getvalue(), content_type = 'image/png')
    response['Content-Length'] = str(len(response.content))
    return response
