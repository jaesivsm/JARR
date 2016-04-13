====
JARR
====

.. image:: https://travis-ci.org/jaesivsm/JARR.svg?branch=master
    :target: https://travis-ci.org/jaesivsm/JARR

.. image:: https://coveralls.io/repos/github/jaesivsm/JARR/badge.svg?branch=master
    :target: https://coveralls.io/github/jaesivsm/JARR?branch=master

Presentation
------------

JARR (which stands for Just Another RSS Reader) is a web-based news aggregator and reader.

JARR is coninuingly ongoing developments and functionnalities are regularly added.
To check on those see the `CHANGELOG <CHANGELOG.rst>`_.
However JARR is stable and can function as easily on a light installation with the python SimpleHTTP server and a SQLite database or on a more heavy setup with nginx or apache running against a PostGreSQL database.

Installing
----------

It's recommended to install JARR inside a virtualenv.

.. code:: bash

    virtualenv venv
    source venv/bin/activate

If you want to connect JARR to your PostgreSQL you'll have to create your database:

.. code:: bash

    sudo -u postgres createuser pgsqluser --no-superuser --createdb --no-createrole
    sudo -u postgres createdb jarr --no-password


.. code:: sql

    ALTER USER '<youruser>' WITH ENCRYPTED PASSWORD '<your password>';
    GRANT ALL PRIVILEGES ON DATABASE aggregator TO '<youruser>';


You'll then have to specify as database URI ``postgres://<your user>:<your password>@127.0.0.1:5433/jarr``. Otherwise you can use the default ``sqlite`` db plug.

Once it's done, execute the script ``install.py``, it will prompt you various configuration values that you'll be able to edit later on in ``src/conf.py`` or by running that script again. If you do so, you may want to run it with the option ``--no-db`` to avoid erasing your already created database (more option are available with ``--help``).

You must then set the crawler to be run once every few minutes with a limited number of feed or once every few hour with all the feeds. I use crontab for that :

.. code:: crontab

    */2 * * * * cd {root};source venv/bin/activate;./manager.py fetch --limit 20 -r


License
-------

JARR is under the `GNU Affero General Public License version 3 <https://www.gnu.org/licenses/agpl-3.0.html>`_.
