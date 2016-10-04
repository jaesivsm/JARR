import logging
import requests.exceptions
from werkzeug.exceptions import BadRequest

from flask import Blueprint, render_template, flash, \
                  redirect, request, url_for
from flask_babel import gettext
from flask_login import login_required, current_user

from web.lib.view_utils import etag_match
from lib.feed_utils import construct_feed_from
from web.controllers import FeedController, ClusterController

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
    feed_contr = FeedController(current_user.id)
    url = (request.args if request.method == 'GET' else request.form)\
            .get('url', None)
    if not url:
        flash(gettext("Couldn't add feed: url missing."), "error")
        raise BadRequest("url is missing")

    feed_exists = list(feed_contr.read(__or__=[{'link': url},
                                               {'site_link': url}]))
    if feed_exists:
        flash(gettext("Didn't add feed: feed already exists."),
              "warning")
        return redirect(url_for('home', at='f', ai=feed_exists[0].id))

    feed = construct_feed_from(url)
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
    """
    List of inactive feeds.
    """
    nb_days = int(request.args.get('nb_days', 365))
    inactives = FeedController(current_user.id).get_inactives(nb_days)
    return render_template('inactives.html',
                           inactives=inactives, nb_days=nb_days)
