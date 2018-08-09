import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import format_timedelta, gettext
from flask_login import current_user, login_required
from sqlalchemy import desc

from jarr_common.utils import redirect_url, utc_now
from jarr.controllers import ClusterController, FeedController, UserController
from jarr.views.common import admin_permission

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def dashboard():
    order = request.args.get('o', 'id')
    reverse = order.startswith('-')
    if reverse:
        order = order[1:]
    if order not in {'login', 'email', 'last_connection', 'is_admin'}:
        order = 'id'
    last_cons, now = {}, utc_now()
    users = list(UserController().read().order_by(
            desc(order) if reverse else order))
    for usr in users:
        last_cons[usr.id] = format_timedelta(now - usr.last_connection)
    return render_template('admin/dashboard.html', now=now, order=order,
            reverse=reverse, last_cons=last_cons, users=users,
            current_user=current_user)


@admin_bp.route('/user/<int:user_id>', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def user(user_id=None):
    """
    See information about a user (stations, etc.).
    """
    usr = UserController().get(id=user_id)
    if usr is None:
        flash(gettext('This user does not exist.'), 'warning')
        return redirect(redirect_url())
    clu_contr = ClusterController(user_id)
    return render_template('/admin/user.html', user=usr,
            feeds=FeedController().read(user_id=user_id).order_by('title'),
            counts=clu_contr.count_by_feed(),
            unread_counts=clu_contr.count_by_feed(read=False))


@admin_bp.route('/toggle_user/<int:user_id>', methods=['GET'])
@login_required
@admin_permission.require()
def toggle_user(user_id=None):
    """
    Enable or disable the account of a user.
    """
    ucontr = UserController()
    usr = ucontr.get(id=user_id)
    user_changed = ucontr.update({'id': user_id},
            {'is_active': not usr.is_active})

    if not user_changed:
        flash(gettext('This user does not exist.'), 'error')
        return redirect(url_for('admin.dashboard'))

    else:
        act_txt = 'activated' if usr.is_active else 'desactivated'
        message = gettext('User %(login)s successfully %(is_active)s',
                          login=usr.login, is_active=act_txt)
    flash(message, 'success')
    return redirect(url_for('admin.dashboard'))
