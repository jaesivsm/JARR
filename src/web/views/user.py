import random

import opml
from flask import (Blueprint, flash, make_response, redirect, render_template,
                   request, url_for)
from flask_babel import gettext
from flask_login import current_user, login_required
from flask_principal import Permission, UserNeed
from werkzeug.exceptions import Forbidden, NotFound

from bootstrap import conf
from lib import emails
from lib.utils import utc_now
from web.controllers import CategoryController, FeedController, UserController
from web.forms import PasswordModForm, ProfileForm, RecoverPasswordForm
from web.views.common import admin_permission, login_user_bundle

users_bp = Blueprint('users', __name__, url_prefix='/users')
user_bp = Blueprint('user', __name__, url_prefix='/user')


def get_contr_and_id(user_id):
    if user_id and admin_permission.can():
        return user_id, UserController()
    elif user_id and Permission(UserNeed(user_id)).can():
        return user_id, UserController(user_id)
    elif user_id:
        flash(gettext('You do not have rights on this user'), 'danger')
        raise Forbidden(gettext('You do not have rights on this user'))
    else:
        return current_user.id, UserController(current_user.id)


@user_bp.route('/opml/export', methods=['GET'])
@login_required
def opml_export():
    user = UserController(current_user.id).get(id=current_user.id)
    categories = {cat.id: cat
            for cat in CategoryController(current_user.id).read()}
    response = make_response(render_template('opml.xml', user=user,
           categories=categories, feeds=FeedController(current_user.id).read(),
           now=utc_now()))
    response.headers['Content-Type'] = 'application/xml'
    response.headers['Content-Disposition'] = 'attachment; filename=feeds.opml'
    return response


@user_bp.route('/opml/import', methods=['POST'])
@login_required
def opml_import():
    if request.files.get('opml.xml', None) is None:
        flash(gettext('Got no file'), 'warning')
        return redirect(url_for('user.profile'))

    data = request.files.get('opml.xml', None)
    try:
        subscriptions = opml.from_string(data.read())
    except Exception:
        flash(gettext("Couldn't parse file"), 'error')
        return redirect(request.referrer)

    ccontr = CategoryController(current_user.id)
    fcontr = FeedController(current_user.id)
    created_count, existing_count, failed_count = 0, 0, 0
    categories = {cat.name: cat.id for cat in ccontr.read()}
    for line in subscriptions:
        try:
            link = line.xmlUrl
        except Exception:
            failed_count += 1
            continue

        # don't import twice
        if fcontr.read(link=link).count():
            existing_count += 1
            continue

        # handling categories
        cat_id = None
        category = getattr(line, 'category', '').lstrip('/')
        if category:
            if category not in categories:
                new_category = ccontr.create(name=category)
                categories[new_category.name] = new_category.id
            cat_id = categories[category]

        fcontr.create(title=getattr(line, 'text', None), category_id=cat_id,
                      description=getattr(line, 'description', None),
                      link=link, site_link=getattr(line, 'htmlUrl', None))
        created_count += 1
    flash(gettext("Created %(created)d feed ! (%(failed)d import failed, "
                  "%(existing)d were already existing)",
                  created=created_count, failed=failed_count,
                  existing=existing_count), "info")
    return redirect(url_for('user.profile'))


def _get_profile_and_pass_form(user_id):
    user_id, ucontr = get_contr_and_id(user_id)
    usr = ucontr.get(id=user_id)
    profile_form, pass_form = ProfileForm(obj=usr), PasswordModForm()
    profile_form.timezone.default = usr.timezone or conf.BABEL_DEFAULT_TIMEZONE
    return usr, ucontr, profile_form, pass_form


@user_bp.route('/profile', methods=['GET'])
@user_bp.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def profile(user_id=None):
    user, _, profile_form, pass_form = _get_profile_and_pass_form(user_id)
    return render_template('profile.html', user=user, form=profile_form,
            admin_permission=admin_permission, pass_form=pass_form)


@user_bp.route('/password_update/<int:user_id>', methods=['POST'])
@login_required
def password_update(user_id):
    user, ucontr, profile_form, pass_form = _get_profile_and_pass_form(user_id)
    if pass_form.validate():
        ucontr.update({'id': user_id}, {'password': pass_form.password.data})

        flash(gettext('Password for %(login)s successfully updated',
                      login=user.login), 'success')
        return redirect(url_for('user.profile', user_id=user.id))
    return render_template('profile.html', user=user, form=profile_form,
            admin_permission=admin_permission, pass_form=pass_form)


@user_bp.route('/profile_update/<int:user_id>', methods=['POST'])
@login_required
def profile_update(user_id):
    user, ucontr, profile_form, pass_form = _get_profile_and_pass_form(user_id)
    if profile_form.validate():
        values = {'login': profile_form.login.data,
                  'email': profile_form.email.data,
                  'timezone': profile_form.timezone.data}
        if admin_permission.can():
            values['is_active'] = profile_form.is_active.data
            values['is_admin'] = profile_form.is_admin.data
            values['is_api'] = profile_form.is_api.data
        ucontr.update({'id': user_id}, values)

        flash(gettext('User %(login)s successfully updated',
                      login=user.login), 'success')
        return redirect(url_for('user.profile', user_id=user.id))
    return render_template('profile.html', user=user, form=profile_form,
            admin_permission=admin_permission, pass_form=pass_form)


@user_bp.route('/delete_account/<int:user_id>', methods=['GET'])
@login_required
def delete(user_id):
    user_id, ucontr = get_contr_and_id(user_id)
    ucontr.delete(user_id)
    flash(gettext('Deletion successful'), 'success')
    if admin_permission.can():
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('login'))


@user_bp.route('/gen_pass_token', methods=['GET', 'POST'])
def gen_recover_token():
    form = RecoverPasswordForm()
    ucontr = UserController()
    if request.method == 'GET':
        return render_template('recover.html', form=form)

    if form.validate():
        token = str(random.getrandbits(128))
        changed = ucontr.update({'email': form.email.data},
                                {'renew_password_token': token})
        if not changed:
            flash(gettext("No user with %(email)r was found"
                          % form.email.data), "danger")
        else:
            body = gettext("""Hello,

A password change request has been made for your account on %(plateform)s.
If you have made that request please follow the link below to renew your
account, otherwise, disregard this email.

%(renew_password_link)s

Regards,

The JARR administrator""", plateform=conf.PLATFORM_URL,
                    renew_password_link=url_for('user.recover',
                        token=token, _external=True))
            emails.send(to=form.email.data, bcc=conf.NOTIFICATION_EMAIL,
                        subject="[jarr] Password renew", plaintext=body)
            flash(gettext("A mail has been sent with a token to renew your "
                          "password"), "info")
    return render_template('recover.html', form=form)


@user_bp.route('/recover/<token>', methods=['GET', 'POST'])
def recover(token):
    form = PasswordModForm()
    ucontr = UserController()
    try:
        user = ucontr.get(renew_password_token=token)
    except NotFound:
        return gettext("Token is not valid, please regenerate one")
    if request.method == 'GET':
        return render_template('recover.html', form=form, token=token)

    if form.validate():
        ucontr.update({'id': user.id},
                {'renew_password_token': '', 'password': form.password.data})
        login_user_bundle(user)
        return redirect(url_for('home'))
    return render_template('recover.html', form=form, token=token)
