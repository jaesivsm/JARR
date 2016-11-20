from functools import lru_cache

from bs4 import BeautifulSoup, SoupStrainer

from lib.utils import jarr_get, rebuild_url

FEED_MIMETYPES = ('application/atom+xml', 'application/rss+xml',
                  'application/rdf+xml', 'application/xml', 'text/xml')


def try_get_icon_url(url, *splits):
    for split in splits:
        if split is None:
            continue
        rb_url = rebuild_url(url, split)
        response = None
        # if html in content-type, we assume it's a fancy 404 page
        try:
            response = jarr_get(rb_url)
            content_type = response.headers.get('content-type', '')
        except Exception:
            pass
        else:
            if response is not None and response.ok \
                    and 'html' not in content_type and response.content:
                return response.url
    return None


@lru_cache(maxsize=None)
def get_soup(content, encoding):
    stype = 'html.parser'
    try:
        head_end = content.find(b'</head>')
        return BeautifulSoup(content[:head_end].decode(encoding), stype)
    except Exception:
        return BeautifulSoup(content, stype, parse_only=SoupStrainer('head'))


def extract_title(response, og_prop='og;title'):
    soup = get_soup(response.content, response.encoding)
    try:
        return soup.find_all('meta', property=og_prop)[0].attrs['content']
    except Exception:
        try:
            return soup.find_all('title')[0].text
        except Exception:
            pass


def extract_tags(response):
    soup = get_soup(response.content, response.encoding)
    tags = set()
    keywords = soup.find_all('meta', {'name': 'keywords'})
    if keywords:
        tags = set(map(str.strip, sum([keyword.attrs['content'].split(',')
                                       for keyword in keywords], [])))
    tags = tags.union({meta.attrs['content']
                       for meta in soup.find_all('meta',
                                                 {'property': 'article:tag'})})
    return {tag.strip() for tag in tags if tag.strip()}


def _check_keys(**kwargs):
    """Returns a callable for BeautifulSoup.find_all add will check existence
    of key and values they hold in the in listed elements.
    """
    def wrapper(elem):
        for key, vals in kwargs.items():
            if not elem.has_attr(key):
                return False
            if not all(val in elem.attrs[key] for val in vals):
                return False
        return True
    return wrapper


def extract_icon_url(response, site_split, feed_split):
    soup = get_soup(response.content, response.encoding)
    icons = soup.find_all(_check_keys(rel=['icon', 'shortcut']))
    if not len(icons):
        icons = soup.find_all(_check_keys(rel=['icon']))
    if len(icons) >= 1:
        for icon in icons:
            icon_url = try_get_icon_url(icon.attrs['href'],
                                        site_split, feed_split)
            if icon_url:
                return icon_url

    icon_url = try_get_icon_url('/favicon.ico', site_split, feed_split)
    if icon_url:
        return icon_url


def extract_feed_link(response, feed_split):
    soup = get_soup(response.content, response.encoding)
    for tpe in FEED_MIMETYPES:
        alternates = soup.find_all(_check_keys(rel=['alternate'], type=[tpe]))
        if len(alternates) >= 1:
            return rebuild_url(alternates[0].attrs['href'], feed_split)
