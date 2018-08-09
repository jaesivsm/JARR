from urllib.parse import ParseResult, unquote, urlparse, urlunparse

from bs4 import BeautifulSoup

from jarr.bootstrap import is_secure_served

HTTPS_IFRAME_DOMAINS = ('vimeo.com', 'youtube.com', 'youtu.be')


def __fix_addr(to_fix, reference, scheme=None):
    scheme = scheme or to_fix.scheme or reference.scheme
    netloc = to_fix.netloc
    if reference:
        netloc = to_fix.netloc or reference.netloc
    return urlunparse(ParseResult(scheme=scheme, netloc=netloc,
                    path=to_fix.path, query=to_fix.query,
                    params=to_fix.params, fragment=to_fix.fragment))


def _handle_img(img, parsed_article_url, fix_readability):
    """Will fix images url being either incompatible with JARR instance or just
    broken."""
    if 'src' not in img.attrs:
        return
    # bug reported to readability, fixing it here for now
    if fix_readability:
        splited_src = unquote(img.attrs['src']).split(', ')
        if len(splited_src) > 1:
            img.attrs['src'] = splited_src[0].split()[0]
    if is_secure_served() and 'srcset' in img.attrs:
        # removing active content when serving over https
        del img.attrs['srcset']
    img_src = urlparse(img.attrs['src'])
    if not img_src.scheme or not img_src.netloc:
        # either scheme or netloc are missing from the src of the img
        img.attrs['src'] = __fix_addr(img_src, parsed_article_url)


def _handle_link(link, parsed_article_url):
    """Will correct href link missing scheme or netloc with scheme or netloc
    from article url."""
    if 'href' not in link.attrs:
        return
    parsed_href = urlparse(link.attrs['href'])
    if not parsed_href.scheme or not parsed_href.netloc:
        link.attrs['href'] = __fix_addr(parsed_href, parsed_article_url)


def _handle_iframe(iframe):
    """Securizing known iframe"""
    if 'src' not in iframe.attrs:
        return
    iframe_src = urlparse(iframe.attrs['src'])
    if iframe_src.scheme != 'http':
        return
    for domain in HTTPS_IFRAME_DOMAINS:
        if domain not in iframe_src.netloc:
            continue
        iframe.attrs['src'] = __fix_addr(iframe_src, None, 'https')


def clean_urls(article_content, article_link, fix_readability=False):
    parsed_article_url = urlparse(article_link)
    parsed_content = BeautifulSoup(article_content, 'html.parser')

    elem_to_parse = 'a', 'img'
    if is_secure_served():
        # iframes are only securized when JARR is served over http
        elem_to_parse += ('iframe',)

    for elem in parsed_content.find_all(elem_to_parse):
        if elem.name == 'a':
            _handle_link(elem, parsed_article_url)
        elif elem.name == 'img':
            _handle_img(elem, parsed_article_url, fix_readability)
        elif elem.name == 'iframe':
            _handle_iframe(elem)
    return str(parsed_content)
