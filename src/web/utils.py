# This file provides functions used for:
# - detection of duplicate articles;
# - import from a JSON file;
# - generation of tags cloud;
# - HTML processing.
#

import re
import sys
import glob
import logging
import operator
import urllib
import itertools
import subprocess
import sqlalchemy
try:
    from urlparse import urlparse, parse_qs, urlunparse
except:
    from urllib.parse import urlparse, parse_qs, urlunparse, urljoin
from datetime import timedelta
from collections import Counter
from contextlib import contextmanager
from flask import request

import conf
from web import controllers
from web.models import Article
from web.lib.utils import clear_string

logger = logging.getLogger(__name__)


def is_safe_url(target):
    """
    Ensures that a redirect target will lead to the same server.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def get_redirect_target():
    """
    Looks at various hints to find the redirect target.
    """
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


@contextmanager
def opened_w_error(filename, mode="r"):
    try:
        f = open(filename, mode)
    except IOError as err:
        yield None, err
    else:
        try:
            yield f, None
        finally:
            f.close()


def fetch(id, feed_id=None):
    """
    Fetch the feeds in a new processus.
    The "asyncio" crawler is launched with the manager.
    """
    cmd = [sys.executable, conf.BASE_DIR + '/manager.py', 'fetch_asyncio',
           str(id), str(feed_id)]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE)


def history(user_id, year=None, month=None):
    """
    Sort articles by year and month.
    """
    articles_counter = Counter()
    articles = controllers.ArticleController(user_id).read()
    if year is not None:
        articles = articles.filter(
                sqlalchemy.extract('year', Article.date) == year)
        if month is not None:
            articles = articles.filter(
                    sqlalchemy.extract('month', Article.date) == month)
    for article in articles.all():
        if year is not None:
            articles_counter[article.date.month] += 1
        else:
            articles_counter[article.date.year] += 1
    return articles_counter, articles


def clean_url(url):
    """
    Remove utm_* parameters
    """
    parsed_url = urlparse(url)
    qd = parse_qs(parsed_url.query, keep_blank_values=True)
    filtered = dict((k, v) for k, v in qd.items()
                                        if not k.startswith('utm_'))
    return urlunparse([
        parsed_url.scheme,
        parsed_url.netloc,
        urllib.parse.quote(urllib.parse.unquote(parsed_url.path)),
        parsed_url.params,
        urllib.parse.urlencode(filtered, doseq=True),
        parsed_url.fragment
    ]).rstrip('=')


def load_stop_words():
    """
    Load the stop words and return them in a list.
    """
    stop_words_lists = glob.glob('./JARR/var/stop_words/*.txt')
    stop_words = []

    for stop_wods_list in stop_words_lists:
        with opened_w_error(stop_wods_list, "r") as (stop_wods_file, err):
            if err:
                stop_words = []
            else:
                stop_words += stop_wods_file.read().split(";")
    return stop_words


def top_words(articles, n=10, size=5):
    """
    Return the n most frequent words in a list.
    """
    stop_words = load_stop_words()
    words = Counter()
    wordre = re.compile(r'\b\w{%s,}\b' % size, re.I)
    for article in articles:
        for word in [elem.lower() for elem in
                wordre.findall(clear_string(article.content))
                if elem.lower() not in stop_words]:
            words[word] += 1
    return words.most_common(n)


def tag_cloud(tags):
    """
    Generates a tags cloud.
    """
    tags.sort(key=operator.itemgetter(0))
    return '\n'.join([('<font size=%d><a href="/search?query=%s" '
                       'title="Count: %s">%s</a></font>' %
                    (min(1 + count * 7 / max([tag[1] for tag in tags]), 7),
                        word, format(count, ',d'), word))
                        for (word, count) in tags])


def compare_documents(feed):
    """
    Compare a list of documents by pair.
    Pairs of duplicates are sorted by "retrieved date".
    """
    duplicates = []
    for pair in itertools.combinations(feed.articles, 2):
        date1, date2 = pair[0].date, pair[1].date
        if clear_string(pair[0].title) == clear_string(pair[1].title) and \
                                        (date1 - date2) < timedelta(days=1):
            if pair[0].retrieved_date < pair[1].retrieved_date:
                duplicates.append((pair[0], pair[1]))
            else:
                duplicates.append((pair[1], pair[0]))
    return duplicates
