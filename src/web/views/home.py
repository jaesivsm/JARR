import pytz
import logging
from datetime import datetime

from flask import (current_app, render_template,
                   request, flash, url_for, redirect)
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext, get_locale
from babel.dates import format_datetime, format_timedelta

from bootstrap import conf
from lib.utils import redirect_url
from web.lib.article_cleaner import clean_urls
from web import utils
from web.lib.view_utils import etag_match
from web.views.common import jsonify

from web.controllers import (UserController, CategoryController,
                             FeedController, ArticleController)

from plugins import readability

localize = pytz.utc.localize
logger = logging.getLogger(__name__)


@current_app.route('/')
@login_required
@etag_match
def home():
    UserController(current_user.id).update({'id': current_user.id},
            {'last_connection': datetime.utcnow()})
    return render_template('home.html')


@current_app.route('/menu')
@login_required
@etag_match
@jsonify
def get_menu():
    now, locale = datetime.now(), get_locale()
    categories_order = [0]
    categories = {0: {'name': 'No category', 'id': 0}}
    for cat in CategoryController(current_user.id).read().order_by('name'):
        categories_order.append(cat.id)
        categories[cat.id] = cat
    unread = ArticleController(current_user.id).count_by_feed(readed=False)
    for cat_id in categories:
        categories[cat_id]['unread'] = 0
        categories[cat_id]['feeds'] = []
    feeds = {feed.id: feed for feed in FeedController(current_user.id).read()}
    for feed_id, feed in feeds.items():
        feed['created_rel'] = format_timedelta(feed.created_date - now,
                add_direction=True, locale=locale)
        feed['last_rel'] = format_timedelta(feed.last_retrieved - now,
                add_direction=True, locale=locale)
        feed['created_date'] = format_datetime(localize(feed.created_date),
                                               locale=locale)
        feed['last_retrieved'] = format_datetime(localize(feed.last_retrieved),
                                                 locale=locale)
        feed['category_id'] = feed.category_id or 0
        feed['unread'] = unread.get(feed.id, 0)
        if not feed.filters:
            feed['filters'] = []
        if feed.icon_url:
            feed['icon_url'] = url_for('icon.icon', url=feed.icon_url)
        categories[feed['category_id']]['unread'] += feed['unread']
        categories[feed['category_id']]['feeds'].append(feed_id)
    return {'feeds': feeds, 'categories': categories,
            'categories_order': categories_order,
            'crawling_method': conf.CRAWLER_TYPE,
            'max_error': conf.FEED_ERROR_MAX,
            'error_threshold': conf.FEED_ERROR_THRESHOLD,
            'is_admin': current_user.is_admin,
            'all_unread_count': sum(unread.values())}


def _get_filters(in_dict):
    query = in_dict.get('query')
    if query:
        search_title = in_dict.get('search_title') == 'true'
        search_content = in_dict.get('search_content') == 'true'
        filters = []
        if search_title:
            filters.append({'title__ilike': "%%%s%%" % query})
        if search_content:
            filters.append({'content__ilike': "%%%s%%" % query})
        if len(filters) == 0:
            filters.append({'title__ilike': "%%%s%%" % query})
        if len(filters) == 1:
            filters = filters[0]
        else:
            filters = {"__or__": filters}
    else:
        filters = {}
    if in_dict.get('filter') == 'unread':
        filters['readed'] = False
    elif in_dict.get('filter') == 'liked':
        filters['like'] = True
    filter_type = in_dict.get('filter_type')
    if filter_type in {'feed_id', 'category_id'} and in_dict.get('filter_id'):
        filters[filter_type] = int(in_dict['filter_id']) or None
    return filters


@jsonify
def _articles_to_json(articles):
    now, locale = datetime.now(), get_locale()
    fd_hash = {feed.id: {'title': feed.title,
                         'icon_url': url_for('icon.icon', url=feed.icon_url)
                                     if feed.icon_url else None}
               for feed in FeedController(current_user.id).read()}

    return {'articles': [{'title': art.title, 'liked': art.like,
            'read': art.readed, 'article_id': art.id, 'selected': False,
            'feed_id': art.feed_id, 'category_id': art.category_id or 0,
            'feed_title': fd_hash[art.feed_id]['title'],
            'icon_url': fd_hash[art.feed_id]['icon_url'],
            'date': format_datetime(localize(art.date), locale=locale),
            'rel_date': format_timedelta(art.date - now,
                    threshold=1.1, add_direction=True,
                    locale=locale)}
            for art in articles.limit(1000)]}


@current_app.route('/middle_panel')
@login_required
@etag_match
def get_middle_panel():
    filters = _get_filters(request.args)
    art_contr = ArticleController(current_user.id)
    articles = art_contr.read_light(**filters)
    return _articles_to_json(articles)


@current_app.route('/getart/<int:article_id>')
@current_app.route('/getart/<int:article_id>/<parse>')
@login_required
@jsonify
def get_article(article_id, parse=False):
    locale = get_locale()
    contr = ArticleController(current_user.id)
    article = contr.get(id=article_id)
    if not article.readed:
        article['readed'] = True
        contr.update({'id': article_id}, {'readed': True})
    article['category_id'] = article.category_id or 0
    feed = FeedController(current_user.id).get(id=article.feed_id)
    article['icon_url'] = url_for('icon.icon', url=feed.icon_url) \
            if feed.icon_url else None
    readability_available = bool(current_user.readability_key
                                 or conf.PLUGINS_READABILITY_KEY)
    article['date'] = format_datetime(localize(article.date), locale=locale)
    article['readability_available'] = readability_available
    if parse or (not article.readability_parsed
            and feed.readability_auto_parse and readability_available):
        try:
            new_content = readability.parse(article.link,
                    current_user.readability_key
                    or conf.PLUGINS_READABILITY_KEY)
        except Exception as error:
            flash("Readability failed with %r" % error, "error")
            article['readability_parsed'] = False
        else:
            article['readability_parsed'] = True
            article['content'] = clean_urls(new_content, article['link'],
                    fix_readability=True)
            new_attr = {'readability_parsed': True, 'content': new_content}
            contr.update({'id': article['id']}, new_attr)
    return article


@current_app.route('/mark_all_as_read', methods=['PUT'])
@login_required
def mark_all_as_read():
    filters = _get_filters(request.json)
    acontr = ArticleController(current_user.id)
    processed_articles = _articles_to_json(acontr.read_light(**filters))
    acontr.update(filters, {'readed': True})
    return processed_articles


@current_app.route('/fetch', methods=['GET'])
@current_app.route('/fetch/<int:feed_id>', methods=['GET'])
@login_required
def fetch(feed_id=None):
    """
    Triggers the download of news.
    News are downloaded in a separated process, mandatory for Heroku.
    """
    if conf.CRAWLING_METHOD == "classic" \
            and (not conf.ON_HEROKU or current_user.is_admin):
        utils.fetch(current_user.id, feed_id)
        flash(gettext("Downloading articles..."), "info")
    else:
        flash(gettext("The manual retrieving of news is only available " +
                      "for administrator, on the Heroku platform."), "info")
    return redirect(redirect_url())
