from flask.ext.wtf import Form
from flask import url_for, redirect
from flask.ext.babel import lazy_gettext
from werkzeug.exceptions import NotFound
from wtforms import TextField, TextAreaField, PasswordField, BooleanField, \
        SubmitField, IntegerField, SelectField, validators, HiddenField
from flask.ext.wtf.html5 import EmailField

from web import utils
from web.controllers import UserController


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
            [validators.Required(lazy_gettext("Please enter a password."))])

    email = EmailField(lazy_gettext("Email"),
            [validators.Length(min=6, max=35),
             validators.Required(
                 lazy_gettext("Please enter your email address."))])
    submit = SubmitField(lazy_gettext("Sign up"))


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
        if not super().validate():
            return False
        ucontr = UserController()
        try:
            user = ucontr.get(login=self.login.data)
        except NotFound:
            self.login.errors.append('Wrong login')
            return False
        if not ucontr.check_password(user, self.password.data):
            self.password.errors.append('Wrong password')
            return False
        self.user = user
        return True


class UserForm(Form):
    """
    Create or edit a user (for the administrator).
    """
    login = TextField(lazy_gettext("Login"),
            [validators.Required(lazy_gettext("Please enter your login"))])
    email = EmailField(lazy_gettext("Email"),
               [validators.Length(min=6, max=35),
                validators.Required(lazy_gettext("Please enter your email."))])
    password = PasswordField(lazy_gettext("Password"))
    refresh_rate = IntegerField(lazy_gettext("Feeds refresh frequency "
                                             "(in minutes)"),
                                default=60)
    submit = SubmitField(lazy_gettext("Save"))


class ProfileForm(Form):
    """
    Edit user information.
    """
    login = TextField(lazy_gettext("Login"),
            [validators.Required(lazy_gettext("Please enter your login"))])
    email = EmailField(lazy_gettext("Email"),
               [validators.Length(min=6, max=35),
                validators.Required(lazy_gettext("Please enter your email."))])
    password = PasswordField(lazy_gettext("Password"))
    password_conf = PasswordField(lazy_gettext("Password Confirmation"))
    refresh_rate = IntegerField(lazy_gettext("Feeds refresh frequency "
                                             "(in minutes)"),
                                default=60)

    readability_key = TextField(lazy_gettext("Readability API key"))
    submit = SubmitField(lazy_gettext("Save"))

    def validate(self):
        validated = super().validate()
        if self.password.data != self.password_conf.data:
            message = lazy_gettext("Passwords aren't the same.")
            self.password.errors.append(message)
            self.password_conf.errors.append(message)
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


class InformationMessageForm(Form):
    subject = TextField(lazy_gettext("Subject"),
            [validators.Required(lazy_gettext("Please enter a subject."))])
    message = TextAreaField(lazy_gettext("Message"),
            [validators.Required(lazy_gettext("Please enter a content."))])
    submit = SubmitField(lazy_gettext("Send"))


class RecoverPasswordForm(Form):
    login = TextField(lazy_gettext("Email"),
            [validators.Required(lazy_gettext("Please enter your login"))])
    submit = SubmitField(lazy_gettext("Recover"))
