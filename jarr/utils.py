# This file provides functions used for:
# - import from a JSON file;
# - generation of tags cloud;
# - HTML processing.
#

import logging

from jarr.lib.utils import jarr_get as common_get
from jarr.bootstrap import conf

logger = logging.getLogger(__name__)


def jarr_get(*args, **kwargs):
    kwargs['timeout'] = conf.crawler.timeout
    kwargs['user_agent'] = conf.crawler.user_agent
    return common_get(*args, **kwargs)


def get_tfidf_pref(feed, pref_name):
    """Tool to figure out clustering setting for a feed.

    For a given feed and a given attribute name will return a boolean
    If this same attribute is set to false on feed's user false will be
    returned, if it's set to false on feed's category false will also be
    returned. If not the value be returned from feed configuration.
    Defaults are set in configurations
    """
    objs = feed.user, feed.category, feed
    for obj in objs:
        if obj is None:
            continue
        if not obj.cluster_conf or pref_name not in obj.cluster_conf:
            continue
        if not obj.cluster_conf[pref_name] and obj is not feed:
            continue
        return obj.cluster_conf.get(pref_name)
    return getattr(conf.clustering.tfidf, pref_name)
