from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import DetailView

from core.utils import DateParser

from meteors.models import Meteor
from meteors.forms import DateForm


@method_decorator(login_required, name = 'dispatch')
class ListView(View):
    def get(self, request):
        time = DateParser(request)   
        context = {
            'meteors': Meteor.objects.filter(lightmaxTime__gte = time.timeFrom, lightmaxTime__lte = time.timeTo),
            'form': DateForm(initial = {'datetime': time.midnight}),
        }
        context.update(time.context())
        return render(request, 'meteors/list-meteors.html', context)

    def post(self, request):
        form = DateForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('listMeteors') + "?date=" + form.cleaned_data['datetime'].strftime("%Y-%m-%d"))
        else:
            return HttpResponseBadRequest()


@login_required
def singleKML(request, name):
    context = {
        'meteor': Meteor.objects.get(name = name)
    }
    return render(request, 'meteors/meteor.kml', context)


@login_required
def singleJSON(request, name):
    meteor = Meteor.objects.get(name = name)
    data = serializers.serialize('json', [meteor])
    return JsonResponse(data, safe = False)


@login_required
def listJSON(request):
    meteors = {}
    for meteor in Meteor.objects.all():
        meteors[meteor.id] = meteor.asDict()

    return JsonResponse(meteors)


@method_decorator(login_required, name = 'dispatch')
class SingleView(DetailView):
    model           = Meteor
    slug_field      = 'name'
    slug_url_kwarg  = 'name'
    template_name   = 'meteors/meteor.html'

#    def get_context_data(self, request, name):
#        context = {
#            'meteor': Meteor.objects.get(name = name),
#        } 
#        return render(request, 'meteors/meteor.html', context)

@method_decorator(csrf_exempt, name = 'dispatch')
class APIView(View):
    def get(self, request):
        return HttpResponse('result')

    def post(self, request):
        print('*' * 20 + " Incoming meteor " + '*' * 20)
        pp(request.POST)
        pp(request.FILES)

        meteor = Meteor.objects.createFromPost(
            timestamp           = request.POST.get('timestamp'),

            beginningLatitude   = request.POST.get('beginningLatitude', None),
            beginningLongitude  = request.POST.get('beginningLongitude', None),
            beginningAltitude   = request.POST.get('beginningAltitude', None),
            beginningTime       = datetime.datetime.strptime(request.POST.get('beginningTime', None), '%Y-%m-%d %H:%M:%S.%f%z'),
            
            lightmaxLatitude    = request.POST.get('lightmaxLatitude', None),
            lightmaxLongitude   = request.POST.get('lightmaxLongitude', None),
            lightmaxAltitude    = request.POST.get('lightmaxAltitude', None),
            lightmaxTime        = datetime.datetime.strptime(request.POST.get('lightmaxTime', None), '%Y-%m-%d %H:%M:%S.%f%z'),

            endLatitude         = request.POST.get('endLatitude', None),
            endLongitude        = request.POST.get('endLongitude', None),
            endAltitude         = request.POST.get('endAltitude', None),
            endTime             = datetime.datetime.strptime(request.POST.get('endTime', None), '%Y-%m-%d %H:%M:%S.%f%z'),

            velocityX           = request.POST.get('velocityX', None),
            velocityY           = request.POST.get('velocityY', None),
            velocityZ           = request.POST.get('velocityZ', None),

            magnitude           = request.POST.get('magnitude', None),
        )
        meteor.save()

        subnetwork = random.choice(Subnetwork.objects.all())
        stationsList = Station.objects.filter(subnetwork__id = subnetwork.id)
        stations = list(filter(lambda x: np.random.uniform(0, 1) > 0.4, stationsList))

        for station in stations:
            Sighting.objects.createForMeteor(meteor, station)       


        print("Meteor has been saved")


        response = HttpResponse('Meteor has been accepted', status = 201)
        response['Location'] = reverse('meteor', args = [meteor.name])
        return response


@method_decorator(csrf_exempt, name = 'dispatch')
class MeteorAPIView(View):
    def get(self, request):
        return HttpResponse('result')

    def post(self, request):
        print('*' * 20 + " Incoming meteor " + '*' * 20)
        pp(request.POST)
        pp(request.FILES)

        meteor = Meteor.objects.createFromPost(
            timestamp           = request.POST.get('timestamp'),

            beginningLatitude   = request.POST.get('beginningLatitude', None),
            beginningLongitude  = request.POST.get('beginningLongitude', None),
            beginningAltitude   = request.POST.get('beginningAltitude', None),
            beginningTime       = datetime.datetime.strptime(request.POST.get('beginningTime', None), '%Y-%m-%d %H:%M:%S.%f%z'),
            
            lightmaxLatitude    = request.POST.get('lightmaxLatitude', None),
            lightmaxLongitude   = request.POST.get('lightmaxLongitude', None),
            lightmaxAltitude    = request.POST.get('lightmaxAltitude', None),
            lightmaxTime        = datetime.datetime.strptime(request.POST.get('lightmaxTime', None), '%Y-%m-%d %H:%M:%S.%f%z'),

            endLatitude         = request.POST.get('endLatitude', None),
            endLongitude        = request.POST.get('endLongitude', None),
            endAltitude         = request.POST.get('endAltitude', None),
            endTime             = datetime.datetime.strptime(request.POST.get('endTime', None), '%Y-%m-%d %H:%M:%S.%f%z'),

            velocityX           = request.POST.get('velocityX', None),
            velocityY           = request.POST.get('velocityY', None),
            velocityZ           = request.POST.get('velocityZ', None),

            magnitude           = request.POST.get('magnitude', None),
        )
        meteor.save()

        subnetwork = random.choice(Subnetwork.objects.all())
        stationsList = Station.objects.filter(subnetwork__id = subnetwork.id)
        stations = list(filter(lambda x: np.random.uniform(0, 1) > 0.4, stationsList))

        for station in stations:
            Sighting.objects.createForMeteor(meteor, station)       


        print("Meteor has been saved")


        response = HttpResponse('Meteor has been accepted', status = 201)
        response['Location'] = reverse('meteor', args = [meteor.name])
        return response
