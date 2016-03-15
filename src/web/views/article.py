from flask import Blueprint, render_template, redirect, flash, url_for
from flask.ext.babel import gettext
from flask.ext.login import login_required, current_user

from web.controllers import ArticleController

articles_bp = Blueprint('articles', __name__, url_prefix='/articles')
article_bp = Blueprint('article', __name__, url_prefix='/article')


@article_bp.route('/redirect/<int:article_id>', methods=['GET'])
@login_required
def redirect_to_article(article_id):
    contr = ArticleController(current_user.id)
    article = contr.get(id=article_id)
    if not article.readed:
        contr.update({'id': article.id}, {'readed': True})
    return redirect(article.link)


def delete(article_id=None):
    "Delete an article from the database."
    article = ArticleController(current_user.id).delete(article_id)
    flash(gettext('Article %(article_title)s deleted',
                  article_title=article.title), 'success')
    return redirect(url_for('home'))


@articles_bp.route('/history', methods=['GET'])
@articles_bp.route('/history/<int:year>', methods=['GET'])
@articles_bp.route('/history/<int:year>/<int:month>', methods=['GET'])
@login_required
def history(year=None, month=None):
    cntr, artcles = ArticleController(current_user.id).get_history(year, month)
    return render_template('history.html', articles_counter=cntr,
                           articles=artcles, year=year, month=month)
