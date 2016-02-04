import os
import logging
import datetime

from bootstrap import application as app, db

from flask import (render_template, flash, session,
                   url_for, redirect, g, current_app)
from flask.ext.login import LoginManager, login_user, logout_user, \
                            login_required, current_user, AnonymousUserMixin
from flask.ext.principal import (Principal, Identity, AnonymousIdentity,
                                 identity_changed, identity_loaded,
                                 RoleNeed, UserNeed)
from flask.ext.babel import gettext
from sqlalchemy.exc import IntegrityError

from web import notifications
from web.forms import SignupForm, SigninForm

from web.controllers import UserController


Principal(app)
# Create a permission with a single Need, in this case a RoleNeed.

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = gettext('Authentication required.')
login_manager.login_message_category = "info"
login_manager.login_view = 'login'

logger = logging.getLogger(__name__)


#
# Management of the user's session.
#
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@login_manager.user_loader
def load_user(id):
    return UserController().get(id=id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log in view.
    """
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('home'))
    g.user = AnonymousUserMixin()
    form = SigninForm()
    if form.validate_on_submit():
        user = UserController().get(login=form.login.data)
        login_user(user)
        identity_changed.send(current_app._get_current_object(),
                              identity=Identity(user.id))
        return form.redirect('home')
    return render_template('login.html', form=form)


@app.route('/logout')
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

    flash(gettext("Logged out successfully."), 'success')
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if int(os.environ.get("SELF_REGISTRATION", 0)) != 1:
        flash(gettext("Self-registration is disabled."), 'warning')
        return redirect(url_for('home'))
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('home'))

    form = SignupForm()

    if form.validate_on_submit():
        user = UserController().create(login=form.login.data,
                    email=form.email.data, password=form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            flash(gettext('Email already used.'), 'warning')
            return render_template('signup.html', form=form)

        # Send the confirmation email
        try:
            notifications.new_account_notification(user)
        except Exception as error:
            flash(gettext('Problem while sending activation email: %(error)s',
                          error=error), 'danger')
            return redirect(url_for('home'))

        flash(gettext('Your account has been created. '
                      'Check your mail to confirm it.'), 'success')
        return redirect(url_for('home'))

    return render_template('signup.html', form=form)
