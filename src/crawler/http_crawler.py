import asyncio
import json
import logging
from functools import partial

import feedparser
import requests

from bootstrap import conf, entry_parsing
from lib import reasons
from lib.article_utils import construct_article, get_skip_and_ids
from lib.feed_utils import construct_feed_from, is_parsing_ok
from lib.utils import default_handler, jarr_get, to_hash, utc_now
from crawler.lib.headers_handling import prepare_headers, extract_feed_info

logger = logging.getLogger(__name__)
logging.captureWarnings(True)
FUTURES = []


def query_jarr(method_name, urn, auth, pool=None, data=None):
    """A wrapper for internal call, method should be ones you can find
    on requests (header, post, get, options, ...), urn the distant
    resources you want to access on jarr, and data, the data you wanna
    transmit."""
    loop = asyncio.get_event_loop()
    if data is None:
        data = {}
    method = getattr(requests, method_name)
    url = "%s%s/%s" % (conf.PLATFORM_URL, conf.API_ROOT.strip('/'), urn)

    future = loop.run_in_executor(None,
            partial(method, url, auth=auth, timeout=conf.CRAWLER_TIMEOUT,
                    data=json.dumps(data, default=default_handler),
                    headers={'Content-Type': 'application/json',
                             'User-Agent': conf.CRAWLER_USER_AGENT}))
    if pool is not None:
        pool.append(future)
    return future


def clean_feed(feed, auth, pool, response, parsed_feed=None, **info):
    """Will reset the errors counters on a feed that have known errors"""
    info.update(extract_feed_info(response.headers, response.text))
    info.update({'error_count': 0, 'last_error': None,
                 'last_retrieved': utc_now()})

    if parsed_feed is not None:  # updating feed with retrieved info
        constructed = construct_feed_from(
                feed['link'], parsed_feed, feed)
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
        return query_jarr('put', 'feed/%d' % feed['id'], auth, pool, info)


def set_feed_error(feed, auth, pool, error=None, parsed_feed=None):
    error_count = feed['error_count'] + 1
    if error:
        last_error = str(error)
    elif parsed_feed:
        last_error = str(parsed_feed.get('bozo_exception', ''))
    if feed['error_count'] > conf.FEED_ERROR_THRESHOLD:
        logger.warning('an error occured while fetching feed; '
                       'bumping error count to %r', error_count)
    info = {'error_count': error_count, 'last_error': last_error,
            'user_id': feed['user_id'], 'last_retrieved': utc_now()}
    info.update(extract_feed_info({}))
    return query_jarr('put', 'feed/%d' % feed['id'], auth, pool, info)


def response_etag_match(feed, resp):
    if feed.get('etag') and resp.headers.get('etag'):
        if feed['etag'].startswith('jarr/'):
            return False  # it's a jarr generated etag
        if resp.headers['etag'] == feed['etag']:
            logger.info("feed responded with same etag (%d)", resp.status_code)
            return True
    return False


def response_calculated_etag_match(feed, resp):
    if ('jarr/"%s"' % to_hash(resp.text)) == feed.get('etag'):
        logger.info("calculated hash matches (%d)", resp.status_code)
        return True
    return False


def challenge(feed, response, auth, no_resp_pool, **kwargs):
    logger.info('cache validation failed, challenging entries')
    parsed = feedparser.parse(response.content.strip())
    if is_parsing_ok(parsed):
        clean_feed(feed, auth, no_resp_pool, response, parsed, **kwargs)
    else:
        set_feed_error(feed, auth, no_resp_pool, parsed_feed=parsed)
        return

    ids, entries, skipped_list = [], {}, []
    for entry in parsed['entries']:
        if not entry:
            continue
        entry_parsing.send('crawler', feed=feed, entry=entry)
        skipped, entry_ids = get_skip_and_ids(entry, feed)
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
    return entries, query_jarr('get', 'articles/challenge',
                               auth, data={'ids': ids})


def add_articles(feed, all_entries, new_entries_ids, auth, no_resp_pool):
    article_created = False
    logger.debug("%d entries wern't matched and will be created",
                 len(new_entries_ids))
    new_articles = []
    for id_to_create in new_entries_ids:
        article_created = True
        new_articles.append(construct_article(
                all_entries[tuple(sorted(id_to_create.items()))], feed))
        logger.info('creating %r for %r - %r', new_articles[-1].get('title'),
                    new_articles[-1].get('user_id'), id_to_create)
    query_jarr('post', 'articles', auth, no_resp_pool, new_articles)

    if not article_created:
        logger.info('all article matched in db, adding nothing')


async def crawl(username, password, **kwargs):
    """entry point, will retreive feeds to be fetch
    and launch the whole thing"""
    logger.debug('Crawler start - retrieving fetchable feed')
    loop = asyncio.get_event_loop()
    auth = username, password
    no_resp_pool = []
    feeds_fetching_pool = []
    challenge_pool = []

    fetchables = await query_jarr('get', 'feeds/fetchable', auth, data=kwargs)

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
                        headers=prepare_headers(feed))))

    for feed, future in zip(feeds, feeds_fetching_pool):
        try:
            resp = await future
            resp.raise_for_status()
        except Exception as error:
            set_feed_error(feed, auth, no_resp_pool, error=error)
            continue

        # checking if cache was validated
        kwargs = {}
        if resp.status_code == 304:
            logger.info('feed responded with 304')
            clean_feed(feed, auth, no_resp_pool, resp,
                       cache_type=reasons.CacheReason.status_code_304.value)
            continue
        elif resp.status_code == 226:
            logger.info('feed responded with 226')
            kwargs['cache_support_a_im'] = True
        elif response_etag_match(feed, resp):
            clean_feed(feed, auth, no_resp_pool, resp,
                       cache_type=reasons.CacheReason.etag.value)
            continue
        elif response_calculated_etag_match(feed, resp):
            clean_feed(feed, auth, no_resp_pool, resp,
                       cache_type=reasons.CacheReason.etag_calculated.value)
            continue
        else:
            logger.debug('etag mismatch %r != %r',
                         resp.headers.get('etag'), feed.get('etag'))

        result = challenge(feed, resp, auth, no_resp_pool, **kwargs)
        if result:
            all_entries, future = result
            challenge_pool.append((future, feed, all_entries))

    for future, feed, all_entries in challenge_pool:
        try:
            resp = await future
            resp.raise_for_status()
        except Exception:
            logger.exception('error while contacting JARR (%r):', resp.content)
            # ignore error on when contacting JARR
            # leave it to the next iteration
            return
        if resp.status_code == 204:
            continue

        new_entries_ids = resp.json()
        add_articles(feed, all_entries, new_entries_ids, auth, no_resp_pool)

    logger.debug("awaiting for all future we're not waiting response from")
    for no_resp_future in no_resp_pool:
        await no_resp_future
    logger.info('Crawler End')


def main(username, password, **kwargs):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawl(username, password, **kwargs))
