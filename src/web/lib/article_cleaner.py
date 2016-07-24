from urllib.parse import urlparse, urlunparse, ParseResult
from bs4 import BeautifulSoup
from bootstrap import is_secure_served

HTTPS_IFRAME_DOMAINS = ('vimeo.com', 'youtube.com', 'youtu.be')


def clean_urls(article_content, article_link):
    parsed_article_url = urlparse(article_link)
    parsed_content = BeautifulSoup(article_content, 'html.parser')

    for img in parsed_content.find_all('img'):
        if 'src' not in img.attrs:
            continue
        if is_secure_served() and 'srcset' in img.attrs:
            # removing active content when serving over https
            del img.attrs['srcset']
        to_rebuild, img_src = False, urlparse(img.attrs['src'])
        if not img_src.scheme or not img_src.netloc:
            to_rebuild = True
            # either scheme or netloc are missing from the src of the img
            scheme = img_src.scheme or parsed_article_url.scheme
            netloc = img_src.netloc or parsed_article_url.netloc
            img_src = ParseResult(scheme=scheme, netloc=netloc,
                    path=img_src.path, query=img_src.query,
                    params=img_src.params, fragment=img_src.fragment)
        if to_rebuild:
            img.attrs['src'] = urlunparse(img_src)

    if is_secure_served():
        for iframe in parsed_content.find_all('iframe'):
            if 'src' not in iframe.attrs:
                continue
            iframe_src = urlparse(iframe.attrs['src'])
            if iframe_src.scheme != 'http':
                continue
            for domain in HTTPS_IFRAME_DOMAINS:
                if domain not in iframe_src.netloc:
                    continue
                iframe_src = ParseResult(scheme='https',
                        netloc=iframe_src.netloc, path=iframe_src.path,
                        query=iframe_src.query, params=iframe_src.params,
                        fragment=iframe_src.fragment)
                iframe.attrs['src'] = urlunparse(iframe_src)
                break
    return str(parsed_content)
