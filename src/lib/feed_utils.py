import html
import urllib
import logging
import feedparser
from bootstrap import conf
from bs4 import BeautifulSoup, SoupStrainer

from lib.utils import try_get_icon_url, rebuild_url, jarr_get

logger = logging.getLogger(__name__)
logging.captureWarnings(True)
FEED_MIMETYPES = ('application/atom+xml', 'application/rss+xml',
                  'application/rdf+xml', 'application/xml', 'text/xml')


def is_parsing_ok(parsed_feed):
    return parsed_feed['entries'] or not parsed_feed['bozo']


def _escape_title_and_desc(feed):
    for key in 'title', 'description':
        if feed.get(key):
            feed[key] = html.unescape(feed[key].strip())
    return feed


def _browse_feedparser_feed(feed, check, default=None):
    if feed.get('feed', {}).get('links') is None:
        return default
    for link in feed['feed']['links']:
        if check(link):
            return link['href']
    return default


def construct_feed_from(url=None, fp_parsed=None, feed=None):
    """
    Will try to construct the most complete feed dict possible.

    url: an url of a feed or a site that might be hosting a feed
    fp_parsed: a feedparser object previously obtained
    feed: an existing feed dict, will be updated
    """
    feed = feed or {'link': url, 'site_link': url}
    if not url and fp_parsed:
        url = fp_parsed.get('href')

    # we'll try to obtain our first parsing from feedparser
    if url and not fp_parsed:
        try:
            fp_parsed = feedparser.parse(url,
                    request_headers={'User-Agent': conf.CRAWLER_USER_AGENT})
        except Exception as error:
            logger.warn('failed to retreive that url: %r', error)
            fp_parsed = {'bozo': 1, 'feed': {}, 'entries': []}
    assert url is not None and fp_parsed is not None

    if not is_parsing_ok(fp_parsed):
        feed['link'] = None

    # updating link
    feed['link'] = _browse_feedparser_feed(fp_parsed,
            lambda link: link['type'] in FEED_MIMETYPES,
            default=feed.get('link'))

    # parsing failed but we obtained a new link to try
    if not is_parsing_ok(fp_parsed) and feed.get('link') != url:
        try:
            fp_parsed = feedparser.parse(feed['link'],
                    request_headers={'User-Agent': conf.CRAWLER_USER_AGENT})
        except Exception as error:
            logger.warn('failed to retreive that url: %r', error)
            fp_parsed = {'bozo': 1, 'feed': {}, 'entries': []}
        url = feed['link']

        if not is_parsing_ok(fp_parsed):
            feed['link'] = None

    # extracting maximum values from parsed feed
    feed['link'] = _browse_feedparser_feed(fp_parsed,
            lambda link: link['type'] in FEED_MIMETYPES,
            default=feed.get('link') or url)
    if fp_parsed['feed'].get('link'):
        feed['site_link'] = fp_parsed['feed']['link']
    else:
        site_link = _browse_feedparser_feed(fp_parsed,
                lambda link: link['rel'] == 'alternate'
                        and link['type'] == 'text/html')
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

    feed['icon_url'] = _browse_feedparser_feed(fp_parsed,
            lambda link: 'icon' in link['rel'], default=feed.get('icon_url'))
    if 'icon_url' not in feed:
        del feed['icon_url']

    # trying to make up for missing values
    feed_split = urllib.parse.urlsplit(url)
    site_split = None
    if not feed.get('site_link') and not feed.get('link'):
        feed['site_link'] = url

    if feed.get('site_link'):
        feed['site_link'] = rebuild_url(feed['site_link'], feed_split)
        site_split = urllib.parse.urlsplit(feed['site_link'])

    if feed.get('icon_url'):
        feed['icon_url'] = try_get_icon_url(
                feed['icon_url'], site_split, feed_split)
        if feed['icon_url'] is None:
            del feed['icon_url']

    nothing_to_fill = all(bool(feed.get(key))
                          for key in ('link', 'title', 'icon_url'))
    # here we have all we want or we do not have the main url,
    # either way we're leaving
    if not feed.get('site_link') or nothing_to_fill:
        return _escape_title_and_desc(feed)

    # trying to parse the page of the site for some rel link in the header
    try:
        response = jarr_get(feed['site_link'])
    except Exception as error:
        logger.warn('failed to retreive %r: %r', feed['site_link'], error)
        return _escape_title_and_desc(feed)
    bs_parsed = BeautifulSoup(response.content, 'html.parser',
                              parse_only=SoupStrainer('head'))

    if not feed.get('title'):
        try:
            feed['title'] = bs_parsed.find_all('title')[0].text
        except Exception:
            pass

    def check_keys(**kwargs):
        def wrapper(elem):
            for key, vals in kwargs.items():
                if not elem.has_attr(key):
                    return False
                if not all(val in elem.attrs[key] for val in vals):
                    return False
            return True
        return wrapper

    if not feed.get('icon_url'):
        icons = bs_parsed.find_all(check_keys(rel=['icon', 'shortcut']))
        if not len(icons):
            icons = bs_parsed.find_all(check_keys(rel=['icon']))
        if len(icons) >= 1:
            for icon in icons:
                feed['icon_url'] = try_get_icon_url(icon.attrs['href'],
                                                    site_split, feed_split)
                if feed['icon_url'] is not None:
                    break

        if feed.get('icon_url') is None:
            feed['icon_url'] = try_get_icon_url('/favicon.ico',
                                                site_split, feed_split)
        if 'icon_url' in feed and feed['icon_url'] is None:
            del feed['icon_url']

    if not feed.get('link'):
        for type_ in FEED_MIMETYPES:
            alternates = bs_parsed.find_all(check_keys(
                    rel=['alternate'], type=[type_]))
            if len(alternates) >= 1:
                feed['link'] = rebuild_url(alternates[0].attrs['href'],
                                           feed_split)
                break
    return _escape_title_and_desc(feed)