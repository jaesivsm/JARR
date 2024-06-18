import random
from datetime import datetime, timezone

from flask import render_template
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                current_user, jwt_required)
from flask_restx import Namespace, Resource, fields
from jarr.api.common import get_ui_url
from jarr.bootstrap import conf
from jarr.controllers import UserController
from jarr.lib import emails
from jarr.lib.utils import get_auth_expiration_delay, utc_now
from jarr.metrics import SERVER
from werkzeug.exceptions import BadRequest, Forbidden

auth_ns = Namespace("auth", description="Auth related operations")
model = auth_ns.model(
    "Login",
    {
        "access_token": fields.String(
            description="The token that must be place "
            "in the Authorization header",
            required=True,
        ),
        "access_token_expires_at": fields.String(required=True),
        "refresh_token": fields.String(),
    },
)
login_parser = auth_ns.parser()
login_parser.add_argument("login", type=str, store_missing=False)
login_parser.add_argument("password", type=str, store_missing=False)
login_init_recovery_parser = auth_ns.parser()
login_init_recovery_parser.add_argument(
    "login", type=str, required=True, store_missing=False
)
login_init_recovery_parser.add_argument(
    "email", type=str, required=True, store_missing=False
)
login_recovery_parser = login_init_recovery_parser.copy()
login_recovery_parser.add_argument(
    "token", type=str, required=True, store_missing=False
)
login_recovery_parser.add_argument(
    "password", type=str, required=True, store_missing=False
)


@auth_ns.route("")
class LoginResource(Resource):
    @staticmethod
    @auth_ns.expect(login_parser)
    @auth_ns.response(200, "OK", model=model)
    @auth_ns.response(400, "Missing params")
    @auth_ns.response(403, "Forbidden")
    def post():
        """Given valid credentials, will provide a token to request the API."""
        attrs = login_parser.parse_args()
        user = UserController().check_password(
            attrs["login"], attrs["password"]
        )
        if not user:
            SERVER.labels(method="post", uri="auth", result="4XX").inc()
            raise Forbidden()
        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)
        UserController(user.id).update(
            {"id": user.id},
            {"last_connection": utc_now(), "renew_password_token": ""},
        )
        SERVER.labels(method="post", uri="/auth", result="2XX").inc()
        return {
            "access_token": f"Bearer {access_token}",
            "refresh_token": f"Bearer {refresh_token}",
            "access_token_expires_at": get_auth_expiration_delay(),
        }, 200


@auth_ns.route("/refresh")
class Refresh(Resource):
    @staticmethod
    @auth_ns.response(200, "OK", model=model)
    @auth_ns.response(403, "Forbidden")
    @jwt_required(refresh=True)
    def post():
        """Given valid credentials, will provide a token to request the API."""
        user = UserController(current_user.id).get(id=current_user.id)
        access_token = create_access_token(identity=user)
        UserController(user.id).update(
            {"id": user.id},
            {"last_connection": utc_now(), "renew_password_token": ""},
        )
        SERVER.labels(method="get", uri="/auth/refresh", result="2XX").inc()
        return {
            "access_token": f"Bearer {access_token}",
            "access_token_expires_at": get_auth_expiration_delay(),
        }, 200


@auth_ns.route("/recovery")
class InitPasswordRecovery(Resource):
    @staticmethod
    @auth_ns.expect(login_init_recovery_parser, validate=True)
    @auth_ns.response(204, "Token generated and mail sent")
    @auth_ns.response(400, "Bad request")
    def post():
        """Initialize password recovery.

        Creates a uniq token and sending a mail with link to recovery page.
        """
        attrs = login_init_recovery_parser.parse_args()
        token = str(random.getrandbits(128))
        changed = UserController().update(
            {"login": attrs["login"], "email": attrs["email"]},
            {"renew_password_token": token},
        )
        if not changed:
            SERVER.labels(
                method="post", uri="/auth/recovery", result="4XX"
            ).inc()
            raise BadRequest(f"No user with {attrs!r} was found")
        BASE_PATH = "auth/recovery/%s/%s/%s"
        landing_url = get_ui_url(
            BASE_PATH % (attrs["login"], attrs["email"], token)
        )

        plaintext = render_template(
            "mail_password_recovery.txt",
            plateform=conf.app.url,
            landing_url=landing_url,
        )
        emails.send(
            to=attrs["email"],
            bcc=conf.notification.email,
            subject="[jarr] Password renew",
            plaintext=plaintext,
        )
        SERVER.labels(method="post", uri="/auth/recovery", result="2XX").inc()
        return None, 204

    @staticmethod
    @auth_ns.expect(login_recovery_parser, validate=True)
    @auth_ns.response(204, "Password updated")
    @auth_ns.response(403, "Wrong token")
    @auth_ns.response(404, "Couldn't find your user")
    def put():
        """Sending new password with recovery token."""
        labels = {"method": "put", "uri": "/auth/recovery"}
        attrs = login_recovery_parser.parse_args()
        try:
            user = UserController().get(
                login=attrs["login"], email=attrs["email"]
            )
        except Exception:
            SERVER.labels(result="4XX", **labels).inc()
            raise
        if (
            not user.renew_password_token
            or not attrs["token"]
            or user.renew_password_token != attrs["token"]
        ):
            SERVER.labels(result="4XX", **labels).inc()
            raise Forbidden()
        result = UserController().update(
            {"id": user.id},
            {"renew_password_token": "", "password": attrs["password"]},
        )
        SERVER.labels(result="2XX" if result else "4XX", **labels).inc()
        return None, 204 if result else 403
