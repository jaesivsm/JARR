import logging
import re
from enum import Enum

logger = logging.getLogger(__name__)
PROCESSED_DATE_KEYS = {'published', 'created', 'updated'}
FETCHABLE_DETAILS = {'link', 'title', 'tags', 'lang'}


class FiltersAction(Enum):
    READ = 'mark as read'
    LIKED = 'mark as favorite'
    SKIP = 'skipped'


class FiltersType(Enum):
    REGEX = 'regex'
    MATCH = 'simple match'
    EXACT_MATCH = 'exact match'
    TAG_MATCH = 'tag match'
    TAG_CONTAINS = 'tag contains'


class FiltersTrigger(Enum):
    MATCH = 'match'
    NO_MATCH = 'no match'


def _is_filter_to_skip(filter_action, only_actions, article):
    if filter_action not in only_actions:
        return True
    if filter_action in {FiltersType.REGEX, FiltersType.MATCH,
            FiltersType.EXACT_MATCH} and 'title' not in article:
        return True
    if filter_action in {FiltersType.TAG_MATCH, FiltersType.TAG_CONTAINS} \
            and 'tags' not in article:
        return True
    return False


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


def process_filters(filters, article, only_actions=None):
    skipped, read, liked = False, None, False
    filters = filters or []
    if only_actions is None:
        only_actions = set(FiltersAction)
    for filter_ in filters:
        filter_action = FiltersAction(filter_.get('action'))

        if _is_filter_to_skip(filter_action, only_actions, article):
            logger.debug('ignoring filter %r', filter_)
            continue

        if not _is_filter_matching(filter_, article):
            continue

        if filter_action is FiltersAction.READ:
            read = True
        elif filter_action is FiltersAction.LIKED:
            liked = True
        elif filter_action is FiltersAction.SKIP:
            skipped = True

    if skipped or read or liked:
        logger.info("%r applied on %r", filter_action.value,
                    article.get('link') or article.get('title'))
    return skipped, read, liked
