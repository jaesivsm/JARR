import logging
import requests.exceptions
from werkzeug.exceptions import BadRequest

from flask import Blueprint, render_template, flash, \
                  redirect, request, url_for
from flask_babel import gettext
from flask_login import login_required, current_user

from bootstrap import conf
from web import utils
from web.lib.view_utils import etag_match
from web.lib.feed_utils import construct_feed_from
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
        flash(gettext("Couldn't add feed: feed already exists."),
                "warning")
        return redirect(url_for('home', at='f', ai=feed_exists[0].id))

    try:
        feed = construct_feed_from(url)
    except requests.exceptions.ConnectionError:
        flash(gettext("Impossible to connect to the address: {}.".format(url)),
              "danger")
        return redirect(url_for('home'))
    except Exception:
        logger.exception('something bad happened when fetching %r', url)
        return redirect(url_for('home'))
    if not feed.get('link'):
        feed['enabled'] = False
        flash(gettext("Couldn't find a feed url, you'll need to find a Atom or"
                      " RSS link manually and reactivate this feed"),
              'warning')
    feed = feed_contr.create(**feed)
    flash(gettext('Feed was successfully created.'), 'success')
    if feed.enabled and conf.CRAWLER_TYPE == "classic":
        utils.fetch(current_user.id, feed.id)
        flash(gettext("Downloading articles for the new feed..."), 'info')
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


@feed_bp.route('/duplicates/<int:feed_id>', methods=['GET'])
@login_required
def duplicates(feed_id):
    """
    Return duplicates article for a feed.
    """
    feed, duplicates = FeedController(current_user.id).get_duplicates(feed_id)
    if len(duplicates) == 0:
        flash(gettext('No duplicates in the feed "{}".').format(feed.title),
                'info')
        return redirect(url_for('home'))
    return render_template('duplicates.html', duplicates=duplicates, feed=feed)
