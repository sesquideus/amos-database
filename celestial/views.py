from django.shortcuts import render
from astropy.coordinates import EarthLocation

def astro(request):
    location = EarthLocation.from_geodetic(17.274021, 48.373273, 531.1)
    context = {
        'geodetic': location.to_geodetic(),
        'geocentric': location.to_geocentric(),
    }
    return render(request, 'astro.html', context)

def error404(request):
    return render(request, '404.html')

# Create your views here.
