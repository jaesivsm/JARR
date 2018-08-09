import logging

from flask import flash, redirect, render_template, request, url_for
from flask_babel import gettext
from flask_principal import PermissionDenied

from jarr.bootstrap import conf
from jarr.lib.view_utils import etag_match

logger = logging.getLogger(__name__)


def load(application):
    @application.errorhandler(401)
    def authentication_required(error):
        if conf.api_root in request.url:
            return error
        return redirect(url_for('login'))

    @application.errorhandler(403)
    def authentication_failed(error):
        if conf.api_root in request.url:
            return error
        flash(gettext('Forbidden.'), 'error')
        return redirect(url_for('login'))

    @application.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404

    @application.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html'), 500

    @application.errorhandler(AssertionError)
    def handle_sqlalchemy_assertion_error(error):
        return error.args[0], 400

    @application.errorhandler(PermissionDenied)
    def handle_permission_denied(error):
        return str(error.args[0]), 403

    @application.route('/about', methods=['GET'])
    @etag_match
    def about():
        return render_template('about.html')

    return (authentication_required,
            authentication_failed,
            page_not_found,
            internal_server_error,
            handle_sqlalchemy_assertion_error,
            handle_permission_denied,
            about)
