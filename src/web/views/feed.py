import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import gettext
from flask_login import current_user, login_required
from werkzeug.exceptions import BadRequest

from lib.feed_utils import construct_feed_from
from web.controllers import ClusterController, FeedController
from web.lib.view_utils import etag_match

logger = logging.getLogger(__name__)
feeds_bp = Blueprint('feeds', __name__, url_prefix='/feeds')
feed_bp = Blueprint('feed', __name__, url_prefix='/feed')


@feeds_bp.route('/', methods=['GET'])
@login_required
@etag_match
def feeds():
    "Lists the subscribed  feeds in a table."
    clu_contr = ClusterController(current_user.id)
    return render_template('feeds.html',
            feeds=FeedController(current_user.id).read(),
            unread_counts=clu_contr.count_by_feed(read=False),
            counts=clu_contr.count_by_feed())


@feed_bp.route('/bookmarklet', methods=['GET', 'POST'])
@login_required
def bookmarklet():
    def check_feeds(link, site_link):
        filters = []
        if link:
            filters.append({'link': link})
        if site_link:
            filters.append({'site_link': site_link})
        filters = {'__or__': filters} if len(filters) > 1 else filters[0]
        feed_exists = feed_contr.read(**filters).first()
        if feed_exists:
            flash(gettext("Didn't add feed: feed already exists."),
                  "warning")
        return feed_exists

    feed_contr = FeedController(current_user.id)
    url = (request.args if request.method == 'GET' else request.form)\
            .get('url', None)

    if not url:
        flash(gettext("Couldn't add feed: url missing."), "error")
        raise BadRequest("url is missing")

    existing_feed = check_feeds(url, url)
    if existing_feed:
        return redirect(url_for('home', at='f', ai=existing_feed.id))

    feed = construct_feed_from(url)

    existing_feed = check_feeds(feed.get('link'), feed.get('link'))
    if existing_feed:
        return redirect(url_for('home', at='f', ai=existing_feed.id))

    if not feed.get('link'):
        feed['enabled'] = False
        flash(gettext("Couldn't find a feed url, you'll need to find a Atom or"
                      " RSS link manually and reactivate this feed"),
              'warning')
    feed = feed_contr.create(**feed)
    flash(gettext('Feed was successfully created.'), 'success')
    return redirect(url_for('home', at='f', ai=feed.id))


@feeds_bp.route('/inactives', methods=['GET'])
@login_required
def inactives():
    nb_days = int(request.args.get('nb_days', 365))
    inactives = FeedController(current_user.id).get_inactives(nb_days)
    return render_template('inactives.html',
                           inactives=inactives, nb_days=nb_days)
