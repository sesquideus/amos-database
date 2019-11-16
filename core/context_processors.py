def main_menu(request):
    return {
        'core': {
            'menu': [
                {'url': 'status',           'caption': 'Status'},
                {'url': 'list-meteors',     'caption': 'Meteors'},
                {'url': 'list-sightings',   'caption': 'Sightings'},
                {'url': 'about',            'caption': 'About'},
                {'url': 'admin:index',      'caption': 'Admin'},
            ]
        }
    }
