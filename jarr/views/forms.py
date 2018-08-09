import pytz
from flask import redirect, url_for
from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from werkzeug.exceptions import NotFound
from wtforms.fields.html5 import EmailField
from wtforms import (BooleanField, HiddenField, PasswordField, SelectField,
                     SubmitField, TextField, validators)

from jarr import utils
from jarr.controllers import UserController


class SignupForm(FlaskForm):
    """
    Sign up form (registration to jarr).
    """
    login = TextField(lazy_gettext("Login"),
            [validators.Required(lazy_gettext("Please enter your login"))])
    password = PasswordField(lazy_gettext("Password"),
            [validators.Required(lazy_gettext("Please enter a password.")),
             validators.Length(min=6, max=100)])
    password_conf = PasswordField(lazy_gettext("Password"),
            [validators.Required(lazy_gettext("Confirm the password."))])

    email = EmailField(lazy_gettext("Email"),
            [validators.Length(min=6, max=35),
             validators.Required(
                 lazy_gettext("Please enter your email address."))])
    # recaptcha = RecaptchaField()

    submit = SubmitField(lazy_gettext("Sign up"))

    def validate(self):
        ucontr = UserController()
        validated = super().validate()
        if ucontr.read(login=self.login.data).count():
            self.login.errors.append('Login already taken')
            validated = False
        if self.password.data != self.password_conf.data:
            self.password_conf.errors.append("Passwords don't match")
            validated = False
        return validated


class RedirectForm(FlaskForm):
    """
    Secure back redirects with WTForms.
    """
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = utils.get_redirect_target() or ''

    def redirect(self, endpoint='home', **values):
        if utils.is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = utils.get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


class SigninForm(RedirectForm):
    login = TextField("Login",
            [validators.Required(lazy_gettext("Please enter your login"))])
    password = PasswordField(lazy_gettext('Password'),
            [validators.Required(lazy_gettext("Please enter a password"))])
    submit = SubmitField(lazy_gettext("Log In"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        validated = super().validate()
        ucontr = UserController()
        try:
            user = ucontr.get(login=self.login.data)
        except NotFound:
            validated = False
        else:
            if not user.is_active:
                validated = False
            if not ucontr.check_password(user, self.password.data):
                validated = False
            self.user = user
        if not validated:
            self.login.errors.append('Invalid credentials.')
        return validated


class ProfileForm(FlaskForm):
    login = TextField(lazy_gettext("Login"),
            [validators.Required(lazy_gettext("Please enter your login"))])
    email = EmailField(lazy_gettext("Email"),
               [validators.Length(min=6, max=35),
                validators.Required(lazy_gettext("Please enter your email."))])
    timezone = SelectField(lazy_gettext("Timezones"),
            choices=[(tz, tz) for tz in pytz.all_timezones])

    readability_key = TextField(lazy_gettext("Readability API key"))
    is_active = BooleanField(lazy_gettext("Activated"), default=True)
    is_admin = BooleanField(lazy_gettext("Is admin"), default=True)
    is_api = BooleanField(lazy_gettext("Has API rights"), default=True)

    submit = SubmitField(lazy_gettext("Save"))


class PasswordModForm(FlaskForm):
    password = PasswordField(lazy_gettext("Password"),
            [validators.Required(lazy_gettext("Please enter a password.")),
             validators.Length(min=6, max=100)])
    password_conf = PasswordField(lazy_gettext("Password confirmation"),
            [validators.Required(lazy_gettext("Confirm the password."))])

    submit = SubmitField(lazy_gettext("Save"))

    def validate(self):
        validated = super().validate()
        if self.password.data != self.password_conf.data:
            self.password_conf.errors.append("Passwords don't match")
            validated = False
        return validated


class CategoryForm(FlaskForm):
    name = TextField(lazy_gettext("Name"))
    submit = SubmitField(lazy_gettext("Submit"))


class RecoverPasswordForm(FlaskForm):
    email = TextField(lazy_gettext("Email"),
            [validators.Required(lazy_gettext("Please enter your email"))])
    submit = SubmitField(lazy_gettext("Submit"))

    def validate(self):
        ucontr = UserController()
        validated = super().validate()
        if not ucontr.read(email=self.email.data).count():
            self.email.errors.append('No user with that email')
            validated = False
        return validated
