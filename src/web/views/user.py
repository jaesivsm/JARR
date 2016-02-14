import opml
import string
import random
from os import path
from datetime import datetime
from werkzeug.exceptions import Forbidden
from flask import (Blueprint, render_template, redirect,
                   flash, url_for, request, make_response)
from flask.ext.principal import Permission, UserNeed
from flask.ext.babel import gettext
from flask.ext.login import current_user, login_required

from web.views.common import admin_permission
from web import notifications
from web.controllers import (UserController, CategoryController,
                             FeedController)

from web.forms import ProfileForm, PasswordModForm, RecoverPasswordForm

users_bp = Blueprint('users', __name__, url_prefix='/users')
user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/opml/export', methods=['GET'])
@login_required
def opml_export():
    user = UserController(current_user.id).get(id=current_user.id)
    categories = {cat.id: cat.dump()
            for cat in CategoryController(current_user.id).read()}
    response = make_response(render_template('opml.xml', user=user,
           categories=categories, feeds=FeedController(current_user.id).read(),
           now=datetime.now()))
    response.headers['Content-Type'] = 'application/xml'
    response.headers['Content-Disposition'] = 'attachment; filename=feeds.opml'
    return response


@user_bp.route('/opml/import', methods=['POST'])
@login_required
def opml_import():
    if request.files.get('opmlfile', None) is None:
        flash(gettext('Got no file'), 'warning')
        return redirect(url_for('user.profile'))

    data = request.files.get('opmlfile', None)
    try:
        subscriptions = opml.from_string(data.read())
    except:
        flash(gettext("Couldn't parse file"), 'danger')
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
        category = getattr(line, 'category', None)
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


@user_bp.route('/profile', methods=['GET'])
@user_bp.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def profile(user_id=None):
    ucontr = None
    if user_id and admin_permission.can():
        ucontr = UserController()
    elif user_id and Permission(UserNeed(user_id)).can():
        ucontr = UserController(user_id)
    elif user_id:
        flash(gettext('You do not have rights on this user'), 'danger')
        raise Forbidden(gettext('You do not have rights on this user'))
    else:
        ucontr = UserController(current_user.id)
        user_id = current_user.id
    user = ucontr.get(id=user_id)
    profile_form, pass_form = ProfileForm(obj=user), PasswordModForm()
    return render_template('profile.html', user=user,
            admin_permission=admin_permission,
            form=profile_form, pass_form=pass_form)


@user_bp.route('/password_update/<int:user_id>', methods=['POST'])
@login_required
def password_update(user_id):
    ucontr = None
    if admin_permission.can():
        ucontr = UserController()
    elif Permission(UserNeed(user_id)).can():
        ucontr = UserController(user_id)
    else:
        flash(gettext('You do not have rights on this user'), 'danger')
        raise Forbidden(gettext('You do not have rights on this user'))
    user = ucontr.get(id=user_id)
    profile_form, pass_form = ProfileForm(obj=user), PasswordModForm()
    if pass_form.validate():
        ucontr.update({'id': user_id}, {'password': pass_form.password.data})

        flash(gettext('Password for %(login)s successfully updated',
                      login=user.login), 'success')
        return redirect(url_for('user.profile', user_id=user.id))

    return render_template('profile.html', user=user,
            admin_permission=admin_permission,
            form=profile_form, pass_form=pass_form)


@user_bp.route('/profile_update/<int:user_id>', methods=['POST'])
@login_required
def profile_update(user_id):
    ucontr = None
    if admin_permission.can():
        ucontr = UserController()
    elif Permission(UserNeed(user_id)).can():
        ucontr = UserController(user_id)
    else:
        flash(gettext('You do not have rights on this user'), 'danger')
        raise Forbidden(gettext('You do not have rights on this user'))
    user = ucontr.get(id=user_id)
    profile_form, pass_form = ProfileForm(obj=user), PasswordModForm()
    if profile_form.validate():
        values = {'login': profile_form.login.data,
                  'email': profile_form.email.data,
                  'refresh_rate': profile_form.refresh_rate.data}
        if admin_permission.can():
            values['is_active'] = profile_form.is_active.data
            values['is_admin'] = profile_form.is_admin.data
            values['is_api'] = profile_form.is_api.data
        ucontr.update({'id': user_id}, values)

        flash(gettext('User %(login)s successfully updated',
                      login=user.login), 'success')
        return redirect(url_for('user.profile', user_id=user.id))

    return render_template('profile.html', user=user,
            admin_permission=admin_permission,
            form=profile_form, pass_form=pass_form)


@user_bp.route('/delete_account/<int:user_id>', methods=['GET'])
@login_required
def delete(user_id):
    ucontr = None
    if admin_permission.can():
        ucontr = UserController()
    elif Permission(UserNeed(user_id)).can():
        ucontr = UserController(user_id)
    else:
        flash(gettext('You do not have rights on this user'), 'danger')
        raise Forbidden(gettext('You do not have rights on this user'))
    ucontr.delete(user_id)
    flash(gettext('Deletion successful'), 'success')
    if admin_permission.can():
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('logout'))


@user_bp.route('/recover', methods=['GET', 'POST'])
def recover():
    """
    Enables the user to recover its account when he has forgotten
    its password.
    """
    form = RecoverPasswordForm()
    user_contr = UserController()

    if request.method == 'POST':
        if form.validate():
            user = user_contr.get(email=form.email.data)
            characters = string.ascii_letters + string.digits
            password = "".join(random.choice(characters)
                               for x in range(random.randint(8, 16)))
            user.set_password(password)
            user_contr.update({'id': user.id}, {'password': password})

            # Send the confirmation email
            try:
                notifications.new_password_notification(user, password)
                flash(gettext('New password sent to your address.'), 'success')
            except Exception as error:
                flash(gettext('Problem while sending your new password: '
                              '%(error)s', error=error), 'danger')

            return redirect(url_for('login'))
        return render_template('recover.html', form=form)

    if request.method == 'GET':
        return render_template('recover.html', form=form)
