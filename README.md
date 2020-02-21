# JARR

[![CircleCI](https://circleci.com/gh/circleci/circleci-docs.svg?style=shield)](https://circleci.com/gh/circleci/circleci-docs)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8b81ef446c4849939796c4965f121ffe)](https://www.codacy.com/manual/francois_7/JARR?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=jaesivsm/JARR&amp;utm_campaign=Badge_Grade)

## Presentation

JARR (which stands for Just Another RSS Reader) is a web-based news aggregator and reader.

JARR is under ongoing developments and functionnalities are regularly added.
For past and futur updates see the [milestones](https://github.com/jaesivsm/JARR/milestones).
However JARR is stable and can function as easily on a light installation with the python SimpleHTTP server and a PostGreSQL database.

## Installing

**to be rewritten at v3**

## Upgrading

The ``master`` branch should always be working and it is recommended you install the project using this one. Partial or unstable change maybe present in the ``develop`` branch even if it'll be avoided as much as we can.
So if you're planning on using the project from the source, you should be using the ``master`` branch only, but, if you're proposing patches, please make your pull request against the ``develop`` branch.

If you have already installed JARR and want to upgrade to a later version, you may encounter some problem if some change have appeared in the model. To fix this, upgrade your database with the following commaned :

```bash

./manager.py db upgrade
```

## License

JARR is under the [GNU Affero General Public License version 3](https://www.gnu.org/licenses/agpl-3.0.html).
