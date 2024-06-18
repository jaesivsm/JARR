import json

from flask import session
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restx import Namespace, Resource
from jarr.api.auth import model
from jarr.api.common import get_ui_url
from jarr.bootstrap import conf
from jarr.controllers import UserController
from jarr.lib.utils import get_auth_expiration_delay, utc_now
from jarr.metrics import SERVER
from rauth import OAuth1Service, OAuth2Service
from werkzeug.exceptions import BadRequest, NotFound, UnprocessableEntity

oauth_ns = Namespace("oauth", description="OAuth related operations")
oauth_callback_parser = oauth_ns.parser()
oauth_callback_parser.add_argument(
    "code", type=str, required=True, store_missing=False
)
oauth1_callback_parser = oauth_ns.parser()
oauth1_callback_parser.add_argument(
    "oauth_verifier", type=str, required=True, store_missing=False
)


# FROM http://blog.miguelgrinberg.com/post/oauth-authentication-with-flask
class OAuthSignInMixin(Resource):  # pragma: no cover
    provider = None  # type: str
    base_url = None  # type: str
    access_token_url = None  # type: str
    authorize_url = None  # type: str

    @property
    def service(self):
        srv_cfg = getattr(conf.oauth, self.provider)
        return OAuth2Service(
            name=self.provider,
            client_id=srv_cfg.id,
            client_secret=srv_cfg.secret,
            base_url=self.base_url,
            access_token_url=self.access_token_url,
            authorize_url=self.authorize_url,
        )

    @classmethod
    def get_callback_url(cls):
        return get_ui_url(f"/oauth/{cls.provider}")

    @classmethod
    def process_ids(cls, social_id, username, email):  # pragma: no cover

        labels = {"method": "get", "uri": "/oauth/callback/" + cls.provider}
        if social_id is None:
            SERVER.labels(result="4XX", **labels).inc()
            raise UnprocessableEntity("No social id, authentication failed")
        ucontr = UserController()
        try:
            user = ucontr.get(**{f"{cls.provider}_identity": social_id})
        except NotFound:
            user = None
        if not user and not conf.oauth.allow_signup:
            SERVER.labels(result="4XX", **labels).inc()
            raise BadRequest("Account creation is not allowed through OAuth.")
        if not user:
            if username and not ucontr.read(login=username).count():
                login = username
            else:
                login = f"{cls.provider}_{username or social_id}"
            new_user = {
                f"{cls.provider}_identity": social_id,
                "login": login,
                "email": email,
            }
            user = ucontr.create(**new_user)
        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)
        ucontr.update(
            {"id": user.id},
            {"last_connection": utc_now(), "renew_password_token": ""},
        )
        SERVER.labels(result="2XX", **labels).inc()
        return {
            "access_token": f"Bearer {access_token}",
            "refresh_token": f"Bearer {refresh_token}",
            "access_token_expires_at": get_auth_expiration_delay(),
        }, 200


class GoogleSignInMixin(OAuthSignInMixin):
    provider = "google"
    base_url = "https://www.googleapis.com/oauth2/v1/"
    access_token_url = "https://accounts.google.com/o/oauth2/token"
    authorize_url = "https://accounts.google.com/o/oauth2/auth"


@oauth_ns.route("/google")
class GoogleAuthorizeUrl(GoogleSignInMixin):

    @oauth_ns.response(301, "Redirect to provider authorize URL")
    def get(self):
        SERVER.labels(
            result="3XX", method="get", uri=f"/oauth/{self.provider}"
        ).inc()
        location = self.service.get_authorize_url(
            scope="email",
            response_type="code",
            redirect_uri=self.get_callback_url(),
        )
        return None, 301, {"Location": location}


@oauth_ns.route("/callback/google")
class GoogleCallback(GoogleSignInMixin):

    @oauth_ns.expect(oauth_callback_parser, validate=True)
    @oauth_ns.response(200, "Authenticate and returns token", model=model)
    @oauth_ns.response(
        400,
        "Identification ended up creating an account "
        "and current configuration doesn't allow it",
    )
    @oauth_ns.response(422, "Auth provider didn't send identity")
    def post(self):
        code = oauth_callback_parser.parse_args()["code"]
        oauth_session = self.service.get_auth_session(
            data={
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.get_callback_url(),
            },
            decoder=lambda x: json.loads(x.decode("utf8")),
        )
        info = oauth_session.get("userinfo").json()
        return self.process_ids(
            info["id"], info.get("name"), info.get("email")
        )


class TwitterSignInMixin(OAuthSignInMixin):
    provider = "twitter"

    @property
    def service(self):
        return OAuth1Service(
            name="twitter",
            consumer_key=conf.oauth.twitter.id,
            consumer_secret=conf.oauth.twitter.secret,
            request_token_url="https://api.twitter.com/oauth/request_token",
            authorize_url="https://api.twitter.com/oauth/authorize",
            access_token_url="https://api.twitter.com/oauth/access_token",
            base_url="https://api.twitter.com/1.1/",
        )


@oauth_ns.route("/twitter")
class TwitterAuthorizeURL(TwitterSignInMixin):

    @oauth_ns.response(301, "Redirect to provider authorize URL")
    def get(self):
        request_token = self.service.get_request_token(
            params={"oauth_callback": self.get_callback_url()}
        )
        session["request_token"] = request_token
        location = self.service.get_authorize_url(request_token[0])
        return None, 301, {"Location": location}


@oauth_ns.route("/twitter")
class TwitterCallback(TwitterSignInMixin):

    @oauth_ns.expect(oauth_callback_parser, validate=True)
    @oauth_ns.response(200, "Authenticate and returns token", model=model)
    @oauth_ns.response(
        400,
        "Identification ended up creating an account "
        "and current configuration doesn't allow it",
    )
    @oauth_ns.response(422, "Auth provider didn't send identity")
    def post(self):
        oauth_verifier = oauth_callback_parser.parse_args()["oauth_verifier"]
        request_token = session.pop("request_token")
        oauth_session = self.service.get_auth_session(
            request_token[0],
            request_token[1],
            data={"oauth_verifier": oauth_verifier},
        )
        info = oauth_session.get("account/verify_credentials.json").json()
        social_id = "twitter$" + str(info.get("id"))
        login = info.get("screen_name")
        return self.process_ids(social_id, login, None)


class FacebookSignInMixin(OAuthSignInMixin):
    provider = "facebook"
    base_url = "https://graph.facebook.com/"
    authorize_url = "https://graph.facebook.com/oauth/authorize"
    access_token_url = "https://graph.facebook.com/oauth/access_token"


@oauth_ns.route("/facebook")
class FacebookAuthorizeUrl(FacebookSignInMixin):

    @oauth_ns.response(301, "Redirect to provider authorize URL")
    def get(self):
        location = self.service.get_authorize_url(
            scope="email",
            response_type="code",
            redirect_uri=self.get_callback_url(),
        )

        return None, 301, {"Location": location}


@oauth_ns.route("/facebook")
class FacebookCallback(FacebookSignInMixin):

    @oauth_ns.expect(oauth_callback_parser, validate=True)
    @oauth_ns.response(200, "Authenticate and returns token", model=model)
    @oauth_ns.response(
        400,
        "Identification ended up creating an account "
        "and current configuration doesn't allow it",
    )
    @oauth_ns.response(422, "Auth provider didn't send identity")
    def post(self):
        code = oauth_callback_parser.parse_args()["code"]
        oauth_session = self.service.get_auth_session(
            data={
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.get_callback_url(),
            }
        )
        info = oauth_session.get("me?fields=id,email").json()
        # Facebook doesn't provide login, so the email is used
        social_id = "facebook$" + info["id"]
        username = info.get("email").split("@")[0]
        email = info.get("email")
        return self.process_ids(social_id, username, email)


class LinuxFrSignInMixin(OAuthSignInMixin):  # pragma: no cover
    provider = "linuxfr"
    base_url = "https://linuxfr.org/"
    authorize_url = "https://linuxfr.org/api/oauth/authorize"
    access_token_url = "https://linuxfr.org/api/oauth/token"


@oauth_ns.route("/linuxfr")
class LinuxfrAuthorizeURL(LinuxFrSignInMixin):

    @oauth_ns.response(301, "Redirect to provider authorize URL")
    def get(self):
        location = self.service.get_authorize_url(
            scope="account",
            response_type="code",
            redirect_uri=self.get_callback_url(),
        )

        return None, 301, {"Location": location}


@oauth_ns.route("/linuxfr")
class LinuxfrCallback(LinuxFrSignInMixin):

    @oauth_ns.expect(oauth_callback_parser, validate=True)
    @oauth_ns.response(200, "Authenticate and returns token", model=model)
    @oauth_ns.response(
        400,
        "Identification ended up creating an account "
        "and current configuration doesn't allow it",
    )
    @oauth_ns.response(422, "Auth provider didn't send identity")
    def post(self):
        code = oauth_callback_parser.parse_args()["code"]
        oauth_session = self.service.get_auth_session(
            data={
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.get_callback_url(),
            },
            decoder=lambda x: json.loads(x.decode("utf8")),
        )
        info = oauth_session.get("api/v1/me").json()
        return self.process_ids(info["login"], info["login"], info["email"])
