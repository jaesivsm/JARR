import pytz
import logging
from datetime import datetime

from flask import current_app, render_template, request, flash, url_for
from flask_login import login_required, current_user
from flask_babel import get_locale
from babel.dates import format_datetime, format_timedelta

from bootstrap import conf
from web.lib.article_cleaner import clean_urls
from web.lib.view_utils import etag_match, clusters_to_json, get_notifications
from web.views.common import jsonify

from web.controllers import (UserController, CategoryController,
                             FeedController, ArticleController,
                             ClusterController)

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
    feeds, categories = {}, {0: {'name': 'No category', 'id': 0,
                                 'feeds': [], 'unread': 0}}
    clu_contr = ClusterController(current_user.id)
    cnt_by_feed = clu_contr.count_by_feed(read=False)
    cnt_by_category = clu_contr.count_by_feed(read=False)
    for cat in CategoryController(current_user.id).read().order_by('name'):
        categories_order.append(cat.id)
        categories[cat.id] = cat
        categories[cat.id]['unread'] = cnt_by_category.get(cat.id, 0)
        categories[cat.id]['feeds'] = []
    for feed in FeedController(current_user.id).read():
        feed['created_rel'] = format_timedelta(feed.created_date - now,
                add_direction=True, locale=locale)
        feed['last_rel'] = format_timedelta(feed.last_retrieved - now,
                add_direction=True, locale=locale)
        feed['created_date'] = format_datetime(localize(feed.created_date),
                                               locale=locale)
        feed['last_retrieved'] = format_datetime(localize(feed.last_retrieved),
                                                 locale=locale)
        feed['category_id'] = feed.category_id or 0
        feed['unread'] = cnt_by_feed.get(feed.id, 0)
        if not feed.filters:
            feed['filters'] = []
        if feed.icon_url:
            feed['icon_url'] = url_for('icon.icon', url=feed.icon_url)
        categories[feed['category_id']]['feeds'].append(feed.id)
        feeds[feed.id] = feed
    return {'feeds': feeds, 'categories': categories,
            'categories_order': categories_order,
            'crawling_method': conf.CRAWLER_TYPE,
            'max_error': conf.FEED_ERROR_MAX,
            'error_threshold': conf.FEED_ERROR_THRESHOLD,
            'is_admin': current_user.is_admin,
            'notifications': get_notifications(),
            'all_unread_count': 0}


def _get_filters(in_dict):
    query = in_dict.get('query')
    if query:
        search_title = in_dict.get('search_title') == 'true'
        search_content = in_dict.get('search_content') == 'true'
        filters = []
        if search_title or len(filters) == 0:
            filters.append({'title__ilike': "%%%s%%" % query})
        if search_content:
            filters.append({'content__ilike': "%%%s%%" % query})
        if len(filters) == 1:
            filters = filters[0]
        else:
            filters = {"__or__": filters}
    else:
        filters = {}
    if in_dict.get('filter') == 'unread':
        filters['read'] = False
    elif in_dict.get('filter') == 'liked':
        filters['liked'] = True
    filter_type = in_dict.get('filter_type')
    if filter_type in {'feed_id', 'category_id'} \
            and (in_dict.get('filter_id') or in_dict.get('filter_id') == 0):
        filters[filter_type] = int(in_dict['filter_id']) or None
    return filters


@current_app.route('/middle_panel')
@login_required
@etag_match
def get_middle_panel():
    return clusters_to_json(ClusterController(current_user.id).join_read(
            **_get_filters(request.args)))


@current_app.route('/getclu/<int:cluster_id>')
@current_app.route('/getclu/<int:cluster_id>/<parse>')
@current_app.route('/getclu/<int:cluster_id>/<parse>/<int:article_id>')
@login_required
@jsonify
def get_cluster(cluster_id, parse=False, article_id=None):
    locale = get_locale()
    artc = ArticleController(current_user.id)
    cluc = ClusterController(current_user.id)
    cluster = cluc.get(id=cluster_id)
    if not cluster.read:
        cluster['read'] = True
        cluc.update({'id': cluster_id}, {'read': True})
    cluster['categories_id'] = cluster.categories_id or []
    feed = FeedController(current_user.id).get(id__in=cluster.feeds_id)
    feed['icon_url'] = url_for('icon.icon', url=feed.icon_url) \
            if feed.icon_url else None
    readability_available = bool(current_user.readability_key
                                 or conf.PLUGINS_READABILITY_KEY)
    cluster['main_date'] = format_datetime(localize(cluster.main_date),
                                           locale=locale)
    if parse or (not cluster.main_article.readability_parsed
            and feed.readability_auto_parse and readability_available):
        if article_id:
            article = next(article for article in cluster.articles
                           if article.id == article_id)
        else:
            article = cluster.main_article
        try:
            new_content = readability.parse(article.link,
                    current_user.readability_key
                    or conf.PLUGINS_READABILITY_KEY)
            new_content = clean_urls(new_content, article['link'],
                                     fix_readability=True)
        except Exception as error:
            flash("Readability failed with %r" % error, "warning")
            article['readability_parsed'] = False
        else:
            article['readability_parsed'] = True
            article['content'] = new_content
            artc.update({'id': article.id},
                        {'readability_parsed': True, 'content': new_content})
    for article in cluster.articles:
        article['readability_available'] = readability_available
    cluster['notifications'] = get_notifications()
    return cluster


@current_app.route('/mark_all_as_read', methods=['PUT'])
@login_required
def mark_all_as_read():
    filters = _get_filters(request.json)
    clu_ctrl = ClusterController(current_user.id)
    clusters = list(clu_ctrl.join_read(**filters))
    if clusters:
        clu_ctrl.update({'id__in': [clu['id'] for clu in clusters]},
                        {'read': True})
    return clusters_to_json(clusters)
