import logging
from datetime import datetime

import conf
from flask import (render_template, flash, session,
                   url_for, redirect, current_app)
from flask.ext.login import LoginManager, login_user, logout_user, \
                            login_required, current_user
from flask.ext.principal import (Principal, Identity, AnonymousIdentity,
                                 identity_changed, identity_loaded,
                                 RoleNeed, UserNeed)
from flask.ext.babel import gettext

from web.forms import SignupForm, SigninForm

from web.controllers import UserController

Principal(current_app)
# Create a permission with a single Need, in this case a RoleNeed.

login_manager = LoginManager()
login_manager.init_app(current_app)
login_manager.login_view = 'login'

logger = logging.getLogger(__name__)


def login_user_bundle(user):
    login_user(user)
    UserController(user.id).update(
                {'id': user.id}, {'last_connection': datetime.utcnow()})
    identity_changed.send(current_app._get_current_object(),
                          identity=Identity(user.id))


@identity_loaded.connect_via(current_app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))
        if current_user.is_admin:
            identity.provides.add(RoleNeed('admin'))
        if current_user.is_api:
            identity.provides.add(RoleNeed('api'))


@login_manager.user_loader
def load_user(user_id):
    return UserController(user_id, ignore_context=True).get(id=user_id)


@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SigninForm()
    if form.validate_on_submit():
        login_user_bundle(form.user)
        return form.redirect('home')
    return render_template('login.html', form=form)


@current_app.route('/logout')
@login_required
def logout():
    # Remove the user information from the session
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    return redirect(url_for('login'))


@current_app.route('/signup', methods=['GET', 'POST'])
def signup():
    if not conf.SELF_REGISTRATION:
        flash(gettext("Self-registration is disabled."), 'warning')
        return redirect(url_for('home'))
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = SignupForm()
    if form.validate_on_submit():
        user = UserController().create(login=form.login.data,
                email=form.email.data, password=form.password.data)
        login_user_bundle(user)
        return redirect(url_for('home'))

    return render_template('signup.html', form=form)
