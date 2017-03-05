import logging

from babel.dates import format_datetime, format_timedelta
from flask import current_app, render_template, request, url_for
from flask_babel import get_locale
from flask_login import current_user, login_required

from bootstrap import conf
from lib.const import UNIX_START
from lib.utils import utc_now
from lib import integrations
from web.controllers import (CategoryController, ClusterController,
                             FeedController, UserController)
from web.lib.view_utils import clusters_to_json, etag_match, get_notifications
from web.views.common import jsonify

logger = logging.getLogger(__name__)


@current_app.route('/')
@login_required
@etag_match
def home():
    UserController(current_user.id).update({'id': current_user.id},
            {'last_connection': utc_now()})
    return render_template('home.html')


@current_app.route('/menu')
@login_required
@etag_match
@jsonify
def get_menu():
    now, locale = utc_now(), get_locale()
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
        feed['created_rel'] = format_timedelta(
                feed.created_date - now, add_direction=True, locale=locale)
        feed['created_date'] = format_datetime(feed.created_date,
                                               locale=locale)
        if feed.last_retrieved == UNIX_START:
            feed['last_rel'] = 'Never fetched'
            feed['last_retrieved'] = ''
        else:
            feed['last_rel'] = format_timedelta(
                    feed.last_retrieved - now,
                    add_direction=True, locale=locale)
            feed['last_retrieved'] = format_datetime(feed.last_retrieved,
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
    clu_contr = ClusterController(current_user.id)
    return clusters_to_json(clu_contr.join_read(**_get_filters(request.args)))


@current_app.route('/getclu/<int:cluster_id>')
@current_app.route('/getclu/<int:cluster_id>/<parse>')
@current_app.route('/getclu/<int:cluster_id>/<parse>/<int:article_id>')
@login_required
@jsonify
def get_cluster(cluster_id, parse=False, article_id=None):
    locale = get_locale()
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
    cluster['main_date'] = format_datetime(cluster.main_date, locale=locale)
    integrations.dispatch('article_parsing', current_user, feed, cluster,
                          mercury_may_parse=True,  # enabling mercury parsing
                          mercury_parse=parse, article_id=article_id)
    for article in cluster.articles:
        article['readability_available'] = readability_available
        article['date'] = format_datetime(article.date, locale=locale)
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
