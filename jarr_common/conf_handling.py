import json
import logging
import os
import random
from os.path import abspath, dirname, join

logger = logging.getLogger(__name__)
ROOT = abspath(join(dirname(globals()['__file__']), '../../..'))
ABS_CHOICES = {'yes': True, 'y': True, 'no': False, 'n': False}
DEFAULT_LOG_LEVEL = 'warn'
SECTIONS = (
        {'options': [
            {'key': 'API_ROOT', 'default': '/api/v2.0', 'edit': False},
            {'key': 'BABEL_DEFAULT_LOCALE', 'default': 'en_GB', 'edit': False},
            {'key': 'BABEL_DEFAULT_TIMEZONE',
             'default': 'Europe/Paris', 'edit': False},
            {'key': 'PLATFORM_URL', 'default': 'http://0.0.0.0:5000/',
             'ask': 'At what address will your installation of JARR '
                    'be available'},
            {'key': 'SQLALCHEMY_DATABASE_URI',
             'ask': 'Enter the database URI',
             'default': 'sqlite+pysqlite:///%s' % join(ROOT, 'jarr.db')},
            {'key': 'TEST_SQLALCHEMY_DATABASE_URI', 'edit': False,
             'default': 'sqlite:///:memory:'},
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
            {'key': 'LEVEL', 'default': DEFAULT_LOG_LEVEL, 'test': 'debug',
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
            {'key': 'TIMEOUT', 'edit': False, 'default': 30},
        ]},
        {'prefix': 'PLUGINS', 'options': [
            {'key': 'READABILITY_KEY', 'default': '',
             'ask': 'Enter your Mercury key key if you have one'},
            {'key': 'RSS_BRIDGE', 'default': '', 'ask': 'Enter the url of the '
             'rss bridge you want to use if you do'},
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
            {'key': 'MIN_EXPIRES',
             'default': 60 * 10, 'type': int, 'edit': False},
            {'key': 'MAX_EXPIRES',
             'default': 60 * 60 * 4, 'type': int, 'edit': False},
            {'key': 'STOP_FETCH', 'default': 30, 'type': int, 'edit': False,
             'ask': "The number of days after which, if a user didn't connect "
                    "we'll stop fetching his feeds, (0 will desactivate this "
                    "feature)"},
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


class ConfObject:
    _paths = ('/etc/jarr.json', '~/.config/jarr.json', 'conf.json')
    log_level_mapping = {'debug': logging.DEBUG,
                         'info': logging.INFO,
                         'warn': logging.WARN,
                         'error': logging.ERROR,
                         'fatal': logging.FATAL}

    @property
    def paths(self):
        for path in self._paths:
            yield os.path.abspath(os.path.expanduser(path))

    def _get_fd(self, mode):
        fd = None
        if sum(os.path.exists(path) for path in self.paths) > 1:
            logger.warning('more than one conf file available in %r, '
                           'will use the first', [path for path in self.paths
                                                  if os.path.exists(path)])
        for path in self.paths:
            try:
                fd = open(path, mode)
                logger.info('will use conf from %r', path)
                return fd
            except PermissionError:
                if os.path.exists(path):
                    logger.warning('permission denied on %s(%s)', path, mode)
            except FileNotFoundError:
                pass

        assert fd is not None, "couldn't find a writable file"

    def reload(self):
        with self._get_fd('r') as fd:
            for key, value in json.load(fd).items():
                setattr(self, key, value)
        self.LOG_LEVEL = self.log_level_mapping[
                getattr(self, 'LOG_LEVEL', DEFAULT_LOG_LEVEL).lower()]
        # filling default missing sections
        for section in SECTIONS:
            for option in section['options']:
                key = get_key(section, option)
                if not hasattr(self, key):
                    setattr(self, key, option['default'])

    def write(self):
        with self._get_fd('w') as fd:
            conf = {}
            for section in SECTIONS:
                for option in section['options']:
                    key = get_key(section, option)
                    conf[key] = getattr(self, key, option['default'])
            reverse_log_level_mapping = {value: key
                    for key, value in self.log_level_mapping.items()}
            conf['LOG_LEVEL'] = reverse_log_level_mapping[conf['LOG_LEVEL']] \
                    if conf.get('LOG_LEVEL') in reverse_log_level_mapping \
                    else DEFAULT_LOG_LEVEL

            json.dump(conf, fd, indent=2, sort_keys=True)
