from flask import Blueprint, render_template, redirect, flash, url_for
from flask_babel import gettext
from flask_login import login_required, current_user

from web.controllers import ArticleController

articles_bp = Blueprint('articles', __name__, url_prefix='/articles')


@articles_bp.route('/history', methods=['GET'])
@articles_bp.route('/history/<int:year>', methods=['GET'])
@articles_bp.route('/history/<int:year>/<int:month>', methods=['GET'])
@login_required
def history(year=None, month=None):
    cntr, artcles = ArticleController(current_user.id).get_history(year, month)
    return render_template('history.html', articles_counter=cntr,
                           articles=artcles, year=year, month=month)
