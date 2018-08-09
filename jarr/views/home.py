import logging

from blinker import signal
from flask import render_template, request, url_for
from flask_login import current_user, login_required

from jarr_common.const import UNIX_START
from jarr_common.utils import utc_now
from jarr_common import reasons
from jarr.bootstrap import conf
from jarr.controllers import (CategoryController, ClusterController,
                              FeedController, UserController)
from jarr.lib.view_utils import clusters_to_json, etag_match, get_notifications
from jarr.views.common import jsonify, fmt_datetime, fmt_timedelta

logger = logging.getLogger(__name__)
article_parsing = signal('article_parsing')


@login_required
@etag_match
def home():
    UserController(current_user.id).update({'id': current_user.id},
            {'last_connection': utc_now()})
    return render_template('home.html')


@login_required
@etag_match
@jsonify
def get_menu():
    now = utc_now()
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
        feed['created_rel'] = fmt_timedelta(feed.created_date - now)
        feed['created_date'] = fmt_datetime(feed.created_date)
        if feed.last_retrieved <= UNIX_START:
            feed['last_rel'] = 'Never fetched'
            feed['last_retrieved'] = ''
        else:
            feed['last_rel'] = fmt_timedelta(feed.last_retrieved - now)
            feed['last_retrieved'] = fmt_datetime(feed.last_retrieved)
        feed['category_id'] = feed.category_id or 0
        feed['unread'] = cnt_by_feed.get(feed.id, 0)
        if not feed.filters:
            feed['filters'] = []
        if feed.icon_url:
            feed['icon_url'] = url_for('icon.get_icon', url=feed.icon_url)
        categories[feed['category_id']]['feeds'].append(feed.id)
        feeds[feed.id] = feed
    return {'feeds': feeds, 'categories': categories,
            'categories_order': categories_order,
            'crawling_method': conf.crawler.type,
            'max_error': conf.feed.error_max,
            'error_threshold': conf.feed.error_threshold,
            'is_admin': current_user.is_admin,
            'notifications': get_notifications(),
            'all_unread_count': 0}


def _get_filters(in_dict):
    """Will extract filters applicable to the JARR controllers from a dict
    either request.json or request.form depending on the use case.
    """
    query = in_dict.get('query')
    if query:
        search_title = in_dict.get('search_title') == 'true'
        search_content = in_dict.get('search_content') == 'true'
        filters = []
        if search_title or not filters:
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


@login_required
@etag_match
def get_middle_panel():
    clu_contr = ClusterController(current_user.id)
    return clusters_to_json(clu_contr.join_read(**_get_filters(request.args)))


@login_required
@jsonify
def get_cluster(cluster_id, parse=False, article_id=None):
    cluc = ClusterController(current_user.id)
    cluster = cluc.get(id=cluster_id)
    if not cluster.read:
        cluster['read'] = True
        cluc.update({'id': cluster_id},
                    {'read': True, 'read_reason': reasons.ReadReason.read})
    cluster['categories_id'] = cluster.categories_id or []
    feed = FeedController(current_user.id).get(id__in=cluster.feeds_id)
    feed['icon_url'] = url_for('icon.get_icon', url=feed.icon_url) \
            if feed.icon_url else None
    readability_available = bool(current_user.readability_key
                                 or conf.plugins.readability_key)
    cluster['main_date'] = fmt_datetime(cluster.main_date)
    article_parsing.send('get_cluster', user=current_user, feed=feed,
                         cluster=cluster,
                         mercury_may_parse=True,  # enabling mercury parsing
                         mercury_parse=parse, article_id=article_id)
    for article in cluster.articles:
        article['readability_available'] = readability_available
        article['date'] = fmt_datetime(article.date)
    cluster['notifications'] = get_notifications()
    return cluster


@login_required
def mark_all_as_read():
    filters = _get_filters(request.json)
    clu_ctrl = ClusterController(current_user.id)
    clusters = list(clu_ctrl.join_read(**filters))
    if clusters:
        clu_ctrl.update({'id__in': [clu['id'] for clu in clusters]},
                        {'read': True,
                         'read_reason': reasons.ReadReason.mass_marked})
    return clusters_to_json(clusters)


def load(application):
    application.route('/')(home)
    application.route('/menu')(get_menu)
    application.route('/middle_panel')(get_middle_panel)

    application.route('/getclu/<int:cluster_id>')(get_cluster)
    application.route('/getclu/<int:cluster_id>/<parse>')(get_cluster)
    application.route(
            '/getclu/<int:cluster_id>/<parse>/<int:article_id>')(get_cluster)
    application.route('/mark_all_as_read', methods=['PUT'])(mark_all_as_read)
