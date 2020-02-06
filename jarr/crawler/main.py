import logging

import feedparser

from ep_celery import celery_app
from jarr.lib import reasons
from jarr.lib.feed_utils import construct_feed_from, is_parsing_ok
from jarr.lib.utils import jarr_get, utc_now
from jarr.bootstrap import conf
from jarr.signals import entry_parsing
from jarr.crawler.requests_utils import (response_etag_match,
        response_calculated_etag_match)
from jarr.crawler.lib.headers_handling import (prepare_headers,
        extract_feed_info)
from jarr.crawler.article import construct_article, get_skip_and_ids
from jarr.controllers import (FeedController, ClusterController,
        ArticleController)

logger = logging.getLogger(__name__)


def clean_feed(feed, response, parsed_feed=None, **info):
    """Will reset the errors counters on a feed that have known errors"""
    info.update(extract_feed_info(response.headers, response.text))
    info.update({'error_count': 0, 'last_error': None,
                 'last_retrieved': utc_now()})

    if parsed_feed is not None:  # updating feed with retrieved info
        constructed = construct_feed_from(feed.link, parsed_feed, feed,
                timeout=conf.crawler.timeout,
                user_agent=conf.crawler.user_agent)
        for key in 'description', 'site_link', 'icon_url':
            if constructed.get(key):
                info[key] = constructed[key]

    info = {key: value for key, value in info.items()
            if getattr(feed, key) != value}

    # updating link on permanent move /redirect
    if response.history and feed.link != response.url and any(
            resp.status_code in {301, 308} for resp in response.history):
        logger.warning('feed moved from %r to %r', feed.link, response.url)
        info['link'] = response.url

    if info:
        return FeedController(feed.user_id).update({'id': feed.id}, info)
    return None


def set_feed_error(feed, error=None, parsed_feed=None):
    error_count = feed.error_count + 1
    if error:
        last_error = str(error)
    elif parsed_feed:
        last_error = str(parsed_feed.get('bozo_exception', ''))
    if feed.error_count > conf.feed.error_threshold:
        level = logging.WARNING
    else:
        level = logging.DEBUG
    logger.log(level, 'an error occured while fetching feed; '
               'bumping error count to %r', error_count)
    logger.debug("last error details %r", last_error)
    info = {'error_count': error_count, 'last_error': last_error,
            'user_id': feed.user_id, 'last_retrieved': utc_now()}
    info.update(extract_feed_info({}))
    return FeedController().update({'id': feed.id}, info)


def create_missing_article(feed, response, **kwargs):
    logger.info('cache validation failed, challenging entries')
    parsed = feedparser.parse(response.content.strip())
    if is_parsing_ok(parsed):
        clean_feed(feed, response, parsed, **kwargs)
    else:
        set_feed_error(feed, parsed_feed=parsed)
        return

    ids, entries, skipped_list = [], {}, []
    for entry in parsed['entries']:
        if not entry:
            continue
        entry_parsing.send('crawler', feed=feed, entry=entry)
        skipped, entry_ids = get_skip_and_ids(entry, feed,
                user_agent=conf.crawler.user_agent,
                resolv=conf.crawler.resolv)
        if skipped:
            skipped_list.append(entry_ids)
            logger.debug('skipping article')
            continue
        entries[tuple(sorted(entry_ids.items()))] = entry
        ids.append(entry_ids)
    if not ids and skipped_list:
        logger.debug('nothing to add (skipped %r) %r', skipped_list, parsed)
        return
    logger.debug('found %d entries %r', len(ids), ids)

    article_created = False
    actrl = ArticleController(feed.user_id)
    new_entries_ids = list(actrl.challenge(ids=ids))
    logger.debug("%d entries wern't matched and will be created",
                 len(new_entries_ids))
    for id_to_create in new_entries_ids:
        article_created = True
        new_article = construct_article(
                entries[tuple(sorted(id_to_create.items()))], feed,
                user_agent=conf.crawler.user_agent,
                resolv=conf.crawler.resolv)
        logger.info('creating %r for %r - %r', new_article.get('title'),
                    new_article.get('user_id'), id_to_create)
        actrl.create(**new_article)

    if not article_created:
        logger.info('all article matched in db, adding nothing')


@celery_app.task(name='crawler.process_feed')
def process_feed(feed_id):
    feed = FeedController().get(id=feed_id)
    logger.debug('%r %r - fetching resources', feed.id, feed.title)
    try:
        resp = jarr_get(feed.link,
                        timeout=conf.crawler.timeout,
                        user_agent=conf.crawler.user_agent,
                        headers=prepare_headers(feed))
        resp.raise_for_status()
    except Exception as error:
        set_feed_error(feed, error=error)
        return

    # checking if cache was validated
    kwargs = {}
    if resp.status_code == 304:
        logger.info('feed responded with 304')
        clean_feed(feed, resp,
                   cache_type=reasons.CacheReason.status_code_304)
    elif resp.status_code == 226:
        logger.info('feed responded with 226')
        kwargs['cache_support_a_im'] = True
    elif response_etag_match(feed, resp):
        clean_feed(feed, resp, cache_type=reasons.CacheReason.etag)
    elif response_calculated_etag_match(feed, resp):
        clean_feed(feed, resp, cache_type=reasons.CacheReason.etag_calculated)
    else:
        logger.debug('etag mismatch %r != %r',
                     resp.headers.get('etag'), feed.etag)
        create_missing_article(feed, resp, **kwargs)


@celery_app.task(name='crawler.clusterizer')
def clusterizer():
    ClusterController.clusterize_pending_articles()


@celery_app.task(name='crawler.scheduler')
def scheduler():
    feeds = list(FeedController().list_fetchable())

    if not feeds:
        logger.debug("No feed to fetch")
        scheduler.apply_async(countdown=conf.crawler.idle_delay)
        return
    logger.debug('%d to fetch', len(feeds))
    for feed in feeds:
        process_feed.apply_async(args=[feed.id])

    clusterizer.apply_async()
    scheduler.apply_async()
