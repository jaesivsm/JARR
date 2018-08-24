from the_conf import TheConf


conf = TheConf({'config_files': ['/etc/jarr.json', '~/.config/jarr.json'],
        'source_order': ['env', 'cmd', 'files'],
        'parameters': [
            {'api_root': {'default': '/api/v2.0'}},
            {'platform_url': {'default': 'http://0.0.0.0:5000/'}},
            {'crawler': [{'login': {'default': 'admin'}},
                         {'passwd': {'default': 'admin'}},
                         {'type': {'default': 'http'}},
                         {'resolv': {'type': bool, 'default': False}},
                         {'user_agent': {
                             'default': 'https://github.com/jaesivsm/JARR'}},
                         {'timeout': {'default': 30, 'type': int}}]},
            {'feed': [{'error_max': {'type': int, 'default': 6}},
                      {'error_threshold': {'type': int, 'default': 3}},
                      {'min_expires': {'type': int, 'default': 60 * 10}},
                      {'max_expires': {'type': int, 'default': 60 * 60 * 4}},
                      {'stop_fetch': {'default': 30, 'type': int}}]},
        ]})
