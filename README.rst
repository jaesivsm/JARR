====
JARR
====

.. image:: https://api.codacy.com/project/badge/Grade/8b81ef446c4849939796c4965f121ffe
   :target: https://www.codacy.com/manual/francois_7/JARR?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=jaesivsm/JARR&amp;utm_campaign=Badge_Grade

.. image:: https://coveralls.io/repos/github/jaesivsm/JARR/badge.svg?branch=develop
    :target: https://coveralls.io/github/jaesivsm/JARR?branch=develop

Presentation
------------

JARR (which stands for Just Another RSS Reader) is a web-based news aggregator and reader.

JARR is under ongoing developments and functionnalities are regularly added.
For past and futur updates see the milestones_.
However JARR is stable and can function as easily on a light installation with the python SimpleHTTP server and a PostGreSQL database.

.. _milestones: https://github.com/jaesivsm/JARR/milestones

Installing
----------

.. code:: bash

    make install


And to create your database:

.. code:: bash

    make init-db


.. code:: sql

    ALTER USER <your user> WITH ENCRYPTED PASSWORD '<your password>';
    GRANT ALL PRIVILEGES ON DATABASE jarr TO '<your user>';

You'll then have to specify as database URI ``postgresql://<your user>:<your password>@127.0.0.1:5432/jarr``.

Once it's done, execute the script ``install.py``, it will prompt you various configuration values that you'll be able to edit later on in ``src/conf.py`` or by running that script again. If you do so, you may want to run it with the option ``--no-db`` to avoid erasing your already created database (more option are available with ``--help``).

**NOTE**: If you don't have ``npm`` installed, the install script won't be able to build the JS file and will propose you to use the one I host on my server. ``npm`` not being available in standard debian installation, I advise you to STFW if you want the JS to be available locally.

**NOTE**: Various OAuth providers are available as authentication provider for JARR. If you want to use those, you can register your JARR application as an app in `google console`_, `facebook applications`_ or `twitter applications`_. Once it's done, you'll have the possibility to set it for JARR through the install process or by editing the ``conf.py`` file.

.. _`google console`: https://console.developers.google.com/apis/library
.. _`facebook applications`: https://www.facebook.com/settings?tab=applications
.. _`twitter applications`: https://apps.twitter.com/app/

You must then set the crawler to be run once every few minutes with a limited number of feed or once every few hour with all the feeds. I use crontab for that :

.. code:: bash

    */2 * * * * cd {root};source venv/bin/activate;./manager.py fetch --limit 20 -r

Upgrading
---------

The ``master`` branch should always be working and it is recommended you install the project using this one. Partial or unstable change maybe present in the ``develop`` branch even if it'll be avoided as much as we can.
So if you're planning on using the project from the source, you should be using the ``master`` branch only, but, if you're proposing patches, please make your pull request against the ``develop`` branch.

If you have already installed JARR and want to upgrade to a later version, you may encounter some problem if some change have appeared in the model. To fix this, upgrade your database with the following commaned :

.. code:: bash

    ./manager.py db upgrade

License
-------

JARR is under the `GNU Affero General Public License version 3 <https://www.gnu.org/licenses/agpl-3.0.html>`_.
