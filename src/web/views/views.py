import logging
import datetime

from bootstrap import application as app

from flask import render_template, request, flash, \
                  url_for, redirect, make_response
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext

from web.lib.utils import redirect_url
from web import export
from web.lib.view_utils import etag_match
from web.controllers import UserController, CategoryController

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
    """
    'About' page.
    """
    return render_template('about.html')


@app.route('/export', methods=['GET'])
@login_required
def export_articles():
    """
    Export all articles to HTML or JSON.
    """
    user = UserController(current_user.id).get(id=current_user.id)
    if request.args.get('format') == "HTML":
        # Export to HTML
        try:
            archive_file, archive_file_name = export.export_html(user)
        except:
            flash(gettext("Error when exporting articles."), 'danger')
            return redirect(redirect_url())
        response = make_response(archive_file)
        response.headers['Content-Type'] = 'application/x-compressed'
        response.headers['Content-Disposition'] = 'attachment; filename=%s' \
                % archive_file_name
    elif request.args.get('format') == "JSON":
        # Export to JSON
        try:
            json_result = export.export_json(user)
        except:
            flash(gettext("Error when exporting articles."), 'danger')
            return redirect(redirect_url())
        response = make_response(json_result)
        response.mimetype = 'application/json'
        response.headers["Content-Disposition"] \
                = 'attachment; filename=account.json'
    else:
        flash(gettext('Export format not supported.'), 'warning')
        return redirect(redirect_url())
    return response


@app.route('/export_opml', methods=['GET'])
@login_required
def export_opml():
    """
    Export all feeds to OPML.
    """
    user = UserController(current_user.id).get(id=current_user.id)
    categories = {cat.id: cat.dump()
            for cat in CategoryController(current_user.id).read()}
    response = make_response(render_template('opml.xml', user=user,
                                            categories=categories,
                                            now=datetime.datetime.now()))
    response.headers['Content-Type'] = 'application/xml'
    response.headers['Content-Disposition'] = 'attachment; filename=feeds.opml'
    return response
