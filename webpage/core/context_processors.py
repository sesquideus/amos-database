def mainMenu(request):
    return {
        'core': {
            'menu': [
                {'url': 'status',           'caption': 'Status'},
                {'url': 'listMeteors',      'caption': 'Meteors'},
                {'url': 'listSightings',    'caption': 'Sightings'},
                {'url': 'about',            'caption': 'About'},
                {'url': 'admin:index',      'caption': 'Admin'},
            ]
        }
    }
