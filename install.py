#!/usr/bin/env python3
import os
import imp
from sys import stderr, path
from subprocess import Popen, PIPE
from argparse import ArgumentParser
root = os.path.join(os.path.dirname(globals()['__file__']), 'src/')
path.append(root)

from lib import conf_handling


REQUIREMENTS = ['aiohttp==0.21.0',
                'alembic==0.8.4',
                'beautifulsoup4==4.4.1',
                'feedparser==5.2.1',
                'Flask==0.10.1',
                'Flask-Babel==0.9',
                'Flask-Login==0.3.2',
                'Flask-Migrate==1.7.0',
                'Flask-Principal==0.4.0',
                'Flask-RESTful==0.3.5',
                'Flask-Script==2.0.5',
                'Flask-SQLAlchemy==2.1',
                'Flask-SSLify==0.1.5',
                'Flask-WTF==0.12',
                'lxml==3.5.0',
                'opml==0.5',
                'python-dateutil==2.4.2',
                'python-postmark==0.4.7',
                'rauth==0.7.2',
                'requests==2.9.1',
                'requests-futures==0.9.5',
                'SQLAlchemy==1.0.11',
                'WTForms==2.1',
                ]
POSTGRES_REQ = 'psycopg2==2.6.1'
DEV_REQUIREMENTS = ['pep8', 'coverage', 'coveralls']


def parse_args():
    parser = ArgumentParser("""This script is aimed to bootstrap JARR.

First of all, it's strongly advise you create a virtualenv before running
this script.

The script will ask you different configuration variables and install JARR
dependencies.
""")
    parser.add_argument('-t', '--test',
                        dest='test', action='store_true', default=False,
                        help="will create configuration with test values (it's"
                             " used in unitests) it won't prompt you anything")
    parser.add_argument('--no-requirements', dest='no_requirements',
                        action='store_true', default=False,
                        help="will create configuration with test values (it's"
                             " used in unitests) it won't prompt you anything")
    parser.add_argument('--no-db', dest='no_database',
                        action='store_true', default=False,
                        help="desactivate the db bootstraping")
    parser.add_argument('--no-js', dest='no_js',
                        action='store_true', default=False,
                        help="won't build js bundle.")
    return parser.parse_args()


def title(text):
    line = '#' * (len(text) + 4)
    print('\n%s\n# %s #\n%s' % (line, text, line))


def can_npm():
    return bool(str(Popen(['which', 'npm'], stdout=PIPE).communicate()[0]))


def ask(text, choices=[], default=None, cast=None):
    while True:
        print(text, end=' ')
        if choices:
            print('[%s]' % '/'.join([chc.upper() if chc == default
                                            or choices[chc] == default else chc
                                     for chc in choices]), end=' ')
        if default not in {'', None}:
            if choices and default not in choices:
                for new_default, value in choices.items():
                    if value == default:
                        default = new_default
                        break
            print('(default: %r)' % default, end=' ')
        print(':', end=' ')

        result = input().lower()
        if not result and default is None:
            print('you must provide an answer')
        elif result and choices and result not in choices:
            print('%r is not in %r' % (result, choices))
        elif not result and default is not None:
            if isinstance(choices, dict):
                return choices[default]
            return default
        elif result:
            if isinstance(choices, dict):
                return choices[result]

            if cast is not None:
                try:
                    result = cast(result)
                except ValueError:
                    print("Couldn't cast %r to %r" % (result, cast))
                    continue
            return result


def build_conf(test=False, creds={}):
    conf, could_import_conf = None, False
    logins, passwords = {'CRAWLER_LOGIN'}, {'CRAWLER_PASSWD'}
    if not test:
        try:
            import conf
            could_import_conf = True
        except ImportError:
            pass
        if not could_import_conf:
            creds['login'] = ask("Admin login", default="admin")
            creds['password'] = ask("Admin password", default="admin")
        else:
            creds['login'] = conf.CRAWLER_LOGIN
            creds['password'] = conf.CRAWLER_PASSWD

    for section in conf_handling.SECTIONS:
        section_edit = section.get('edit', True)
        if not test and section_edit and 'ask' in section:
            print()
            section_edit = ask(section['ask'],
                    choices=conf_handling.ABS_CHOICES, default='no')
        prefix = section.get('prefix', '')
        if not test and section_edit and prefix:
            title(prefix)
        for option in section['options']:
            edit = section_edit and option.get('edit', True)

            name = conf_handling.get_key(section, option)

            if test and 'test' in option:
                default = option['test']
            elif could_import_conf and hasattr(conf, name):
                default = getattr(conf, name)
            elif name == 'BUNDLE_JS' and can_npm():
                default = 'local'
            else:
                default = option.get('default')

            if (edit and not test) \
                    or (name == 'BUNDLE_JS' and not can_npm()):
                value = ask(option['ask'], choices=option.get('choices', []),
                            default=default)
            else:
                value = default
            if 'type' in option:
                value = option['type'](value)
            if name in logins and creds.get('login'):
                value = creds['login']
            if name in passwords and creds.get('password'):
                value = creds['password']
            yield prefix, name, value
    print()


def install_python_deps(args):
    try:
        import pip
    except ImportError:
        print('pip is not available ; aborting', file=stderr)

    import conf
    imp.reload(conf)
    if not args.no_requirements:
        install_postgres = 'postgres' in conf.SQLALCHEMY_DATABASE_URI

    print('installing python dependencies...')
    pip.main(['install', '--quiet', '--upgrade'] + REQUIREMENTS)
    if install_postgres:
        pip.main(['install', '--quiet', '--upgrade', POSTGRES_REQ])
    if args.test:
        pip.main(['install', '--quiet', '--upgrade'] + DEV_REQUIREMENTS)


def bootstrap_database(args, creds):
    if not args.no_database and not args.test:
        print('bootstraping databases...')
        import manager
        manager.db_empty()
        manager.db_create(creds['login'], creds['password'])


def init_submodule():
    print('initializing submodules...')
    Popen(['git', 'submodule', 'init'], stdout=PIPE).wait()
    Popen(['git', 'submodule', 'update'], stdout=PIPE).wait()


def build_bundle_js(args):
    if not args.no_js and can_npm():
        print('building JS bundle...')
        Popen(['npm', 'run', 'build'], stdout=PIPE, stderr=PIPE).wait()


def main():
    args = parse_args()
    creds = {}
    new_conf = list(build_conf(args.test, creds))
    conf_handling.write_conf(new_conf)
    install_python_deps(args)
    bootstrap_database(args, creds)
    init_submodule()
    build_bundle_js(args)


if __name__ == '__main__':
    main()
