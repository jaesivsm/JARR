import logging
import re
from enum import Enum

logger = logging.getLogger(__name__)


class FiltersAction(Enum):
    READ = 'mark as read'
    UNREAD = 'mark as unread'
    LIKED = 'mark as favorite'
    UNLIKED = 'mark as unliked'
    SKIP = 'skipped'
    UNSKIPPED = 'unskipped'
    ALLOW_CLUSTERING = 'allow clustering'
    DISALLOW_CLUSTERING = 'disallow clustering'


class FiltersType(Enum):
    REGEX = 'regex'
    MATCH = 'simple match'
    EXACT_MATCH = 'exact match'
    TAG_MATCH = 'tag match'
    TAG_CONTAINS = 'tag contains'


class FiltersTrigger(Enum):
    MATCH = 'match'
    NO_MATCH = 'no match'


def _is_filter_matching(filter_, article):
    pattern = filter_.get('pattern', '')
    filter_type = FiltersType(filter_.get('type'))
    filter_trigger = FiltersTrigger(filter_.get('action on'))
    title = article.get('title', '')
    if filter_type is not FiltersType.REGEX:
        pattern = pattern.lower()
        title = title.lower()
    tags = [tag.lower() for tag in article.get('tags', [])]
    if filter_type is FiltersType.REGEX:
        match = re.match(pattern, title)
    elif filter_type is FiltersType.MATCH:
        match = pattern in title
    elif filter_type is FiltersType.EXACT_MATCH:
        match = pattern == title
    elif filter_type is FiltersType.TAG_MATCH:
        match = pattern in tags
    elif filter_type is FiltersType.TAG_CONTAINS:
        match = any(pattern in tag for tag in tags)
    return match and filter_trigger is FiltersTrigger.MATCH \
            or not match and filter_trigger is FiltersTrigger.NO_MATCH


def _alter_result(filter_action, filter_result):
    if filter_action is FiltersAction.READ:
        filter_result['read'] = True
    if filter_action is FiltersAction.UNREAD:
        filter_result['read'] = False
    elif filter_action is FiltersAction.LIKED:
        filter_result['liked'] = True
    elif filter_action is FiltersAction.UNLIKED:
        filter_result['liked'] = False
    elif filter_action is FiltersAction.SKIP:
        filter_result['skipped'] = True
    elif filter_action is FiltersAction.UNSKIPPED:
        filter_result['skipped'] = False
    elif filter_action is FiltersAction.ALLOW_CLUSTERING:
        filter_result['clustering'] = True
    elif filter_action is FiltersAction.DISALLOW_CLUSTERING:
        filter_result['clustering'] = False


def process_filters(filters, article, only_actions=None):
    keys = 'skipped', 'clustering', 'read', 'liked'
    defaults = False, True, None, False
    filter_result = dict(zip(keys, defaults))
    filters = filters or []
    if only_actions is None:
        only_actions = set(FiltersAction)
    for filter_ in filters:
        filter_action = FiltersAction(filter_.get('action'))
        if _is_filter_matching(filter_, article):
            _alter_result(filter_action, filter_result)

    if any(filter_result[key] != defaults[i] for i, key in enumerate(keys)):
        logger.info('processing filters resulted on %s for Art(f=%s, eid=%r)',
                    ', '.join(['%s=%s' % (key, value)
                               for key, value in filter_result.items()]),
                    article.get('feed_id'), article.get('entry_id'))

    return filter_result
