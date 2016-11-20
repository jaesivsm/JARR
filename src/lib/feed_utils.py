import html
import logging
import urllib
from copy import deepcopy

import feedparser

from bootstrap import conf
from lib.utils import jarr_get, rebuild_url
from lib.html_parsing import (extract_title, extract_icon_url, FEED_MIMETYPES,
                              extract_feed_link, try_get_icon_url)

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


def is_parsing_ok(parsed_feed):
    return parsed_feed['entries'] or not parsed_feed['bozo']


def correct_feed_values(func):
    to_escape = {'title', 'description'}

    def wrapper(*args, **kwargs):
        feed = {k: v for k, v in func(*args, **kwargs).items() if v}
        for key in to_escape.intersection(feed):
            if feed.get(key):
                feed[key] = html.unescape(feed[key].strip())
        return feed
    return wrapper


def _browse_feedparser_feed(feed, check, default=None):
    if not feed.get('feed', {}).get('links'):
        yield default
        return
    returned = False
    for link in feed['feed']['links']:
        if check(link):
            returned = True
            yield link['href']
    if not returned:
        yield default


def get_parsed_feed(url):
    try:
        fp_parsed = feedparser.parse(url,
                request_headers={'User-Agent': conf.CRAWLER_USER_AGENT})
    except Exception as error:
        logger.warn('failed to retreive that url: %r', error)
        fp_parsed = {'bozo': 1, 'feed': {}, 'entries': []}
    return fp_parsed


@correct_feed_values
def construct_feed_from(url=None, fp_parsed=None, feed=None):
    """
    Will try to construct the most complete feed dict possible.

    url: an url of a feed or a site that might be hosting a feed
    fp_parsed: a feedparser object previously obtained
    feed: an existing feed dict, will be updated
    """
    feed = deepcopy(feed) if feed else {}
    if not url and hasattr(fp_parsed, 'get') and fp_parsed.get('href'):
        url = fp_parsed.get('href')

    # we'll try to obtain our first parsing from feedparser
    if url and not fp_parsed:
        fp_parsed = get_parsed_feed(url)
    assert url is not None and fp_parsed is not None

    if is_parsing_ok(fp_parsed):
        feed['link'] = url
    else:
        # trying to get link url from data parsed by feedparser
        feed['link'] = next(_browse_feedparser_feed(fp_parsed,
                lambda link: link['type'] in FEED_MIMETYPES,
                default=feed.get('link')))
        if feed['link'] and feed['link'] != url:
            # trying newly got url
            fp_parsed = get_parsed_feed(feed['link'])
            if not is_parsing_ok(fp_parsed):  # didn't work, no link found
                feed['link'] = None
        feed['site_link'] = url

    if fp_parsed['feed'].get('link'):
        feed['site_link'] = fp_parsed['feed']['link']
    else:
        site_link = next(_browse_feedparser_feed(fp_parsed,
                lambda link: link['rel'] == 'alternate'
                        and link['type'] == 'text/html'))
        feed['site_link'] = site_link or feed.get('site_link')
        feed['site_link'] = feed['site_link'] or feed.get('link')

    if not feed.get('title'):  # not overriding user pref for title
        if fp_parsed['feed'].get('title'):
            feed['title'] = fp_parsed['feed'].get('title')
        elif fp_parsed['feed'].get('title_detail', {}).get('value'):
            feed['title'] = fp_parsed['feed']['title_detail']['value']

    if fp_parsed['feed'].get('summary'):
        feed['description'] = fp_parsed['feed']['summary']
    elif fp_parsed['feed'].get('subtitle_detail', {}).get('value'):
        feed['description'] = fp_parsed['feed']['subtitle_detail']['value']

    # trying to make up for missing values
    feed_split = urllib.parse.urlsplit(url)
    site_split = None
    if feed.get('site_link'):
        feed['site_link'] = rebuild_url(feed['site_link'], feed_split)
        site_split = urllib.parse.urlsplit(feed['site_link'])

    new_icon_urls = [fp_parsed.get('feed', {}).get('icon')] \
                    + list(_browse_feedparser_feed(fp_parsed,
                           lambda link: 'icon' in link['rel']))
    if feed.get('icon_url') not in new_icon_urls:
        for icon_url in new_icon_urls:
            if not icon_url:
                continue
            icon_url = try_get_icon_url(icon_url, site_split, feed_split)
            if icon_url:
                feed['icon_url'] = icon_url
                break

    nothing_to_fill = all(bool(feed.get(key))
                          for key in ('link', 'title', 'icon_url'))
    # here we have all we want or we do not have the main url,
    # either way we're leaving
    if not feed.get('site_link') or nothing_to_fill:
        return feed

    # trying to parse the page of the site for some rel link in the header
    try:
        response = jarr_get(feed['site_link'])
    except Exception as error:
        logger.warn('failed to retreive %r: %r', feed['site_link'], error)
        return feed

    if not feed.get('title'):
        feed['title'] = extract_title(response, og_prop='og:site_name')

    if not feed.get('icon_url'):
        feed['icon_url'] = extract_icon_url(response, site_split, feed_split)

    if not feed.get('link'):
        feed['link'] = extract_feed_link(response, feed_split)
    return feed
