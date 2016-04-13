#!/usr/bin/env python3
"""This script will print on stdout a valid apache conf
according to your configuration."""
import os
from os.path import join, abspath, dirname
import sys
from urllib.parse import urlparse

TEMPLATE = """
<VirtualHost *:443>
    ServerName {domain}
    SSLEngine on

    WSGIScriptAlias / {entry_point}
    WSGIDaemonProcess rsss processes=4 threads=10 python-path={path!r}
    WSGIProcessGroup rsss
    WSGIApplicationGroup %{{GLOBAL}}
    WSGIScriptReloading On
    WSGIPassAuthorization On

    DocumentRoot {document_root!r}
    <Directory {directory}>
        Options Indexes FollowSymLinks MultiViews
        AllowOverride All All
        Order allow,deny
        allow from all
    </Directory>

    ErrorLog ${{APACHE_LOG_DIR}}/error.log
    CustomLog ${{APACHE_LOG_DIR}}/jarr-access.log vhost_combined
    LogLevel warn
</VirtualHost>
"""

root = abspath(join(dirname(globals()['__file__']), 'src/'))
sys.path.append(root)
import conf

def main():
    if os.environ.get('VIRTUAL_ENV'):
        path = "%s:%s" % (root, join(os.environ['VIRTUAL_ENV'],
                                     'lib/python3.4/site-packages'))
    else:
        path = root

    print(TEMPLATE.format(domain=urlparse(conf.PLATFORM_URL).netloc,
                          entry_point=abspath(join(root, 'runserver.py')),
                          document_root=root, directory=root, path=path))


if __name__ == '__main__':
    main()
