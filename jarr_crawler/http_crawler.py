import asyncio
import logging
from functools import partial

import feedparser

from jarr_common import reasons
from jarr_common.feed_utils import construct_feed_from, is_parsing_ok
from jarr_common.utils import jarr_get, utc_now
from jarr_crawler.bootstrap import conf
from jarr_crawler.signals import entry_parsing
from jarr_crawler.requests_utils import (query_jarr, response_etag_match,
        response_calculated_etag_match)
from jarr_crawler.lib.headers_handling import (prepare_headers,
        extract_feed_info)
from jarr_crawler.article import construct_article, get_skip_and_ids

logger = logging.getLogger(__name__)
logging.captureWarnings(True)
FUTURES = []


def clean_feed(feed, pool, response, parsed_feed=None, **info):
    """Will reset the errors counters on a feed that have known errors"""
    info.update(extract_feed_info(response.headers, response.text))
    info.update({'error_count': 0, 'last_error': None,
                 'last_retrieved': utc_now()})

    if parsed_feed is not None:  # updating feed with retrieved info
        constructed = construct_feed_from(feed['link'], parsed_feed, feed,
                timeout=conf.crawler.timeout,
                user_agent=conf.crawler.user_agent)
        for key in 'description', 'site_link', 'icon_url':
            if constructed.get(key):
                info[key] = constructed[key]

    info = {key: value for key, value in info.items()
            if feed.get(key) != value}

    # updating link on permanent move /redirect
    if response.history and feed['link'] != response.url and any(
            resp.status_code in {301, 308} for resp in response.history):
        logger.warning('feed moved from %r to %r', feed['link'], response.url)
        info['link'] = response.url

    if info:
        return query_jarr('put', 'feed/%d' % feed['id'], pool, info)
    return None


def set_feed_error(feed, pool, error=None, parsed_feed=None):
    error_count = feed['error_count'] + 1
    if error:
        last_error = str(error)
    elif parsed_feed:
        last_error = str(parsed_feed.get('bozo_exception', ''))
    if feed['error_count'] > conf.feed.error_threshold:
        level = logging.WARNING
    else:
        level = logging.DEBUG
    logger.log(level, 'an error occured while fetching feed; '
               'bumping error count to %r', error_count)
    logger.debug("last error details %r", last_error)
    info = {'error_count': error_count, 'last_error': last_error,
            'user_id': feed['user_id'], 'last_retrieved': utc_now()}
    info.update(extract_feed_info({}))
    return query_jarr('put', 'feed/%d' % feed['id'], pool, info)


def challenge(feed, response, no_resp_pool, **kwargs):
    logger.info('cache validation failed, challenging entries')
    parsed = feedparser.parse(response.content.strip())
    if is_parsing_ok(parsed):
        clean_feed(feed, no_resp_pool, response, parsed, **kwargs)
    else:
        set_feed_error(feed, no_resp_pool, parsed_feed=parsed)
        return None, None

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
        return None, None
    logger.debug('found %d entries %r', len(ids), ids)
    return entries, query_jarr('get', 'articles/challenge', data={'ids': ids})


def add_articles(feed, all_entries, new_entries_ids, no_resp_pool):
    article_created = False
    logger.debug("%d entries wern't matched and will be created",
                 len(new_entries_ids))
    new_articles = []
    for id_to_create in new_entries_ids:
        article_created = True
        new_articles.append(construct_article(
                all_entries[tuple(sorted(id_to_create.items()))], feed,
                user_agent=conf.crawler.user_agent,
                resolv=conf.crawler.resolv))
        logger.info('creating %r for %r - %r', new_articles[-1].get('title'),
                    new_articles[-1].get('user_id'), id_to_create)
    promise = query_jarr('post', 'articles', no_resp_pool, new_articles)

    if not article_created:
        logger.info('all article matched in db, adding nothing')
    return promise


async def iter_on_feeds(feeds, feeds_fetching_pool, no_resp_pool):
    challenge_pool = []
    for feed, future in zip(feeds, feeds_fetching_pool):
        try:
            resp = await future
            resp.raise_for_status()
        except Exception as error:
            set_feed_error(feed, no_resp_pool, error=error)
            continue

        # checking if cache was validated
        kwargs = {}
        if resp.status_code == 304:
            logger.info('feed responded with 304')
            clean_feed(feed, no_resp_pool, resp,
                       cache_type=reasons.CacheReason.status_code_304.value)
            continue
        elif resp.status_code == 226:
            logger.info('feed responded with 226')
            kwargs['cache_support_a_im'] = True
        elif response_etag_match(feed, resp):
            clean_feed(feed, no_resp_pool, resp,
                       cache_type=reasons.CacheReason.etag.value)
            continue
        elif response_calculated_etag_match(feed, resp):
            clean_feed(feed, no_resp_pool, resp,
                       cache_type=reasons.CacheReason.etag_calculated.value)
            continue
        else:
            logger.debug('etag mismatch %r != %r',
                         resp.headers.get('etag'), feed.get('etag'))

        result = challenge(feed, resp, no_resp_pool, **kwargs)
        if result:
            all_entries, future = result
            challenge_pool.append((future, feed, all_entries))
    return challenge_pool


async def iter_on_entries(challenge_pool, no_resp_pool):
    pool = []
    for future, feed, all_entries in challenge_pool:
        try:
            resp = await future
            resp.raise_for_status()
        except Exception:
            logger.exception('error while contacting JARR (%r):', resp.content)
            # ignore error on when contacting JARR
            # leave it to the next iteration
            continue
        if resp.status_code == 204:
            continue

        new_entries_ids = resp.json()
        pool.append(add_articles(feed, all_entries, new_entries_ids,
                no_resp_pool))
    return pool


async def iter_on_cluster(article_pool, no_resp_pool):
    for future, cluster_read, cluster_liked in article_pool:
        try:
            resp = await future
            resp.raise_for_status()
        except Exception:
            logger.exception('error while contacting JARR (%r):', resp.content)
            continue
        new_article = resp.json()
        query_jarr('post', 'cluster/clusterize', no_resp_pool,
                data={'article_id': new_article['id'],
                      'cluster_read': cluster_read,
                      'cluster_liked': cluster_liked})


async def crawl(**kwargs):
    """entry point, will retreive feeds to be fetch
    and launch the whole thing"""
    logger.debug('Crawler start - retrieving fetchable feed')
    loop = asyncio.get_event_loop()
    no_resp_pool = []
    feeds_fetching_pool = []

    fetchables = await query_jarr('get', 'feeds/fetchable', data=kwargs)

    # processes feeds that need to be fetched
    try:
        fetchables.raise_for_status()
    except Exception:
        logger.exception('Something went wrong when retrieving feeds:')
        return
    if fetchables.status_code == 204:
        logger.debug("No feed to fetch")
        return
    feeds = fetchables.json()
    logger.debug('%d to fetch', len(feeds))
    for feed in feeds:
        logger.debug('%r %r - fetching resources', feed['id'], feed['title'])
        feeds_fetching_pool.append(loop.run_in_executor(None,
                partial(jarr_get, feed['link'],
                        timeout=conf.crawler.timeout,
                        user_agent=conf.crawler.user_agent,
                        headers=prepare_headers(feed))))

    challenge_pool = iter_on_feeds(feeds, feeds_fetching_pool, no_resp_pool)
    article_pool = iter_on_entries(challenge_pool, no_resp_pool)
    iter_on_cluster(article_pool, no_resp_pool)

    logger.debug("awaiting for all future we're not waiting response from")
    for no_resp_future in no_resp_pool:
        await no_resp_future
    logger.info('Crawler End')


def main(**kwargs):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawl(**kwargs))
