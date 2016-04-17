import os
from os.path import abspath, join, dirname
import random

ROOT = abspath(join(dirname(globals()['__file__']), '../..'))
ABS_CHOICES = {'yes': True, 'y': True, 'no': False, 'n': False}
SECTIONS = (
        {'options': [
            {'key': 'API_ROOT', 'default': '/api/v2.0', 'edit': False},
            {'key': 'LANGUAGES', 'edit': False,
             'default': {'en': 'English', 'fr': 'French'}},
            {'key': 'TIME_ZONE', 'edit': False,
             'default': {'en': 'US/Eastern', 'fr': 'Europe/Paris'}},
            {'key': 'PLATFORM_URL', 'default': 'http://0.0.0.0:5000/',
             'ask': 'At what address will your installation of JARR '
                    'be available'},
            {'key': 'SQLALCHEMY_DATABASE_URI',
             'ask': 'Enter the database URI',
             'default': 'sqlite+pysqlite:///%s' % join(ROOT, 'jarr.db'),
             'test': 'sqlite:///:memory:'},
            {'key': 'SQLALCHEMY_TRACK_MODIFICATIONS',
             'edit': False, 'default': True, 'type': bool},
            {'key': 'SECRET_KEY', 'edit': False,
             'default': str(random.getrandbits(128))},
            {'key': 'ON_HEROKU', 'edit': False, 'default': True, 'type': bool},
            {'key': 'BUNDLE_JS', 'edit': False,
             'default': 'http://filer.1pxsolidblack.pl/'
                        'public/jarr/current.min.js',
             'ask': 'You seem not to be able to build the js bundle for JARR'
                    ', you must provide the url of a builded one'},
        ]},
        {'prefix': 'LOG', 'edit': False, 'options': [
            {'key': 'LEVEL', 'default': 'warn', 'test': 'debug',
             'choices': ('debug', 'info', 'warn', 'error', 'fatal')},
            {'key': 'TYPE', 'default': ''},
            {'key': 'PATH', 'default': ''},
        ]},
        {'prefix': 'CRAWLER', 'edit': False, 'options': [
            {'key': 'LOGIN', 'default': 'admin'},
            {'key': 'PASSWD', 'default': 'admin'},
            {'key': 'NBWORKER', 'type': int, 'default': 2, 'test': 1},
            {'key': 'TYPE', 'default': 'http', 'edit': False},
            {'key': 'RESOLV', 'type': bool, 'default': False,
             'choices': ABS_CHOICES, 'edit': False},
            {'key': 'USER_AGENT',
             'edit': False, 'default': 'https://github.com/jaesivsm/JARR'},
        ]},
        {'prefix': 'PLUGINS', 'options': [
            {'key': 'READABILITY_KEY', 'default': '',
             'ask': 'Enter your readability key if you have one'},
        ]},
        {'prefix': 'AUTH', 'options': [
            {'key': 'ALLOW_SIGNUP', 'default': True, 'type': bool,
             'choices': ABS_CHOICES,
             'ask': 'Do you want to allow people to create account '
                    'with passwords'},
            {'key': 'RECAPTCHA_USE_SSL', 'default': True, 'edit': False},
            {'key': 'RECAPTCHA_PUBLIB_KEY', 'default': '',
             'ask': 'If you have a recaptcha public key enter it'},
            {'key': 'RECAPTCHA_PRIVATE_KEY', 'default': '',
             'ask': 'If you have a recaptcha private key enter it'},
        ]},
        {'ask': 'Do you want to configure third party OAUTH provider',
         'prefix': 'OAUTH', 'options': [
                {'key': 'ALLOW_SIGNUP', 'default': True, 'type': bool,
                 'choices': ABS_CHOICES,
                 'ask': 'Do you want to allow people to create account through'
                       ' third party OAUTH provider'},
                {'key': 'TWITTER_ID', 'default': '',
                 'ask': 'Enter your twitter id if you have one'},
                {'key': 'TWITTER_SECRET', 'default': '',
                 'ask': 'Enter your twitter secret if you have one'},
                {'key': 'FACEBOOK_ID', 'default': '',
                 'ask': 'Enter your facebook id if you have one'},
                {'key': 'FACEBOOK_SECRET', 'default': '',
                 'ask': 'Enter your facebook secret if you have one'},
                {'key': 'GOOGLE_ID', 'default': '',
                 'ask': 'Enter your google id if you have one'},
                {'key': 'GOOGLE_SECRET', 'default': '',
                 'ask': 'Enter your google secret if you have one'},
                {'key': 'LINUXFR_ID', 'default': '',
                 'ask': 'Enter your linuxfr id if you have one'},
                {'key': 'LINUXFR_SECRET', 'default': '',
                 'ask': 'Enter your linuxfr secret if you have one'},
                ]},
        {'prefix': 'NOTIFICATION', 'edit': False, 'options': [
            {'key': 'EMAIL', 'default': ''},
            {'key': 'HOST', 'default': 'smtp.googlemail.com'},
            {'key': 'STARTTLS', 'type': bool,
             'default': True, 'choices': ABS_CHOICES},
            {'key': 'PORT', 'type': int, 'default': 587},
            {'key': 'LOGIN', 'default': ''},
            {'key': 'PASSWORD', 'default': ''},
        ]},

        {'prefix': 'FEED', 'edit': False, 'options': [
            {'key': 'ERROR_MAX', 'type': int, 'default': 6, 'edit': False},
            {'key': 'ERROR_THRESHOLD',
             'type': int, 'default': 3, 'edit': False},
            {'key': 'REFRESH_RATE',
             'default': 60, 'type': int, 'edit': False},
        ]},
        {'prefix': 'WEBSERVER', 'edit': False, 'options': [
            {'key': 'HOST', 'default': '0.0.0.0', 'edit': False},
            {'key': 'PORT', 'default': 5000, 'type': int, 'edit': False},
        ]},
)


def get_key(section, option):
    name = section.get('prefix', '')
    if name:
        name += '_'
    return name + option['key']


def write_conf(conf_gen):
    current_section = None
    in_src = 'bootstrap.py' in os.listdir()
    path = 'conf.py' if in_src else 'src/conf.py'
    with open(path, 'w') as fd:
        for section, key, value in conf_gen:
            if current_section != section and section:
                fd.write('\n# %s\n' % section.upper())
            current_section = section
            fd.write('%s = %r\n' % (key, value))


def rewrite(new_conf):
    import imp
    import conf

    def browse():
        for section in SECTIONS:
            for option in section['options']:
                key = get_key(section, option)
                if key in new_conf:
                    value = new_conf[key]
                elif hasattr(conf, key):
                    value = getattr(conf, key)
                else:
                    value = option.get('default')
                yield section.get('prefix'), key, value
    write_conf(browse())
    imp.reload(conf)
