import logging

from bootstrap import application as app

from flask import render_template, flash, url_for, redirect
from flask.ext.babel import gettext

from web.lib.view_utils import etag_match

logger = logging.getLogger(__name__)


#
# Custom error pages.
#
@app.errorhandler(401)
def authentication_required(e):
    flash(gettext('Authentication required.'), 'info')
    return redirect(url_for('login'))


@app.errorhandler(403)
def authentication_failed(e):
    flash(gettext('Forbidden.'), 'danger')
    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


@app.route('/about', methods=['GET'])
@etag_match
def about():
    return render_template('about.html')
