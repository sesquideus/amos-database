def mainMenu(request):
    return {
        'core': {
            'menu': [
                {'url': 'status',           'caption': 'Status'},
                {'url': 'listMeteors',      'caption': 'All meteors'},
                {'url': 'listSightings',    'caption': 'All sightings'},
                {'url': 'about',            'caption': 'About'},
                {'url': 'admin:index',      'caption': 'Admin'},
            ]
        }
    }
