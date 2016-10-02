from flask_wtf import Form
from flask import url_for, redirect
from flask_babel import lazy_gettext
from werkzeug.exceptions import NotFound
from wtforms import TextField, PasswordField, BooleanField, \
                    SubmitField, SelectField, validators, HiddenField
from flask_wtf.html5 import EmailField

from web import utils
from web.controllers import UserController
# from flask_wtf import RecaptchaField


class SignupForm(Form):
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


class RedirectForm(Form):
    """
    Secure back redirects with WTForms.
    """
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
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
            self.login.errors.append('Wrong login')
            validated = False
        else:
            if not user.is_active:
                self.login.errors.append('User is desactivated')
                validated = False
            if not ucontr.check_password(user, self.password.data):
                self.password.errors.append('Wrong password')
                validated = False
            self.user = user
        return validated


class ProfileForm(Form):
    login = TextField(lazy_gettext("Login"),
            [validators.Required(lazy_gettext("Please enter your login"))])
    email = EmailField(lazy_gettext("Email"),
               [validators.Length(min=6, max=35),
                validators.Required(lazy_gettext("Please enter your email."))])

    readability_key = TextField(lazy_gettext("Readability API key"))
    is_active = BooleanField(lazy_gettext("Activated"), default=True)
    is_admin = BooleanField(lazy_gettext("Is admin"), default=True)
    is_api = BooleanField(lazy_gettext("Has API rights"), default=True)

    submit = SubmitField(lazy_gettext("Save"))


class PasswordModForm(Form):
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


class AddFeedForm(Form):
    title = TextField(lazy_gettext("Title"), [validators.Optional()])
    link = TextField(lazy_gettext("Feed link"),
            [validators.Required(lazy_gettext("Please enter the URL."))])
    site_link = TextField(lazy_gettext("Site link"), [validators.Optional()])
    enabled = BooleanField(lazy_gettext("Check for updates"), default=True)
    submit = SubmitField(lazy_gettext("Save"))
    category_id = SelectField(lazy_gettext("Category of the feed"),
                              [validators.Optional()])

    def set_category_choices(self, categories):
        self.category_id.choices = [('0', 'No Category')]
        self.category_id.choices += [(str(cat.id), cat.name)
                                      for cat in categories]


class CategoryForm(Form):
    name = TextField(lazy_gettext("Name"))
    submit = SubmitField(lazy_gettext("Submit"))


class RecoverPasswordForm(Form):
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
