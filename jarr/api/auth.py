import random
from urllib.parse import SplitResult, urlsplit, urlunsplit

from flask import current_app, render_template
from flask_restx import Namespace, Resource, fields
from werkzeug.exceptions import BadRequest, Forbidden

from jarr.bootstrap import conf
from jarr.controllers import UserController
from jarr.lib import emails
from jarr.lib.utils import utc_now

auth_ns = Namespace("auth", description="Auth related operations")
model = auth_ns.model("Login", {
    "access_token": fields.String(description="The token that must be place "
                                              "in the Authorization header"),
})
login_parser = auth_ns.parser()
login_parser.add_argument("login", type=str, required=True)
login_parser.add_argument("password", type=str, required=True)
login_init_recovery_parser = auth_ns.parser()
login_init_recovery_parser.add_argument("login", type=str, required=True)
login_init_recovery_parser.add_argument("email", type=str, required=True)
login_recovery_parser = login_init_recovery_parser.copy()
login_recovery_parser.add_argument("token", type=str, required=True)
login_recovery_parser.add_argument("password", type=str, required=True)


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
        jwt = current_app.extensions["jwt"]
        user = jwt.authentication_callback(attrs["login"], attrs["password"])
        if not user:
            raise Forbidden()
        access_token = jwt.jwt_encode_callback(user)
        UserController(user.id).update({"id": user.id},
                                       {"last_connection": utc_now(),
                                        "renew_password_token": ""})
        return {"access_token": "%s %s" % (conf.auth.jwt_header_prefix,
                                           access_token.decode("utf8"))}, 200


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
        changed = UserController().update({"login": attrs["login"],
                                           "email": attrs["email"]},
                                          {"renew_password_token": token})
        if not changed:
            raise BadRequest("No user with %r was found" % attrs)
        BASE_PATH = '%s/auth/recovery/%s/%s/%s'
        split = urlsplit(conf.app.url)
        split = SplitResult(scheme=split.scheme,
                            netloc=split.netloc,
                            path=BASE_PATH % (split.path, attrs["login"],
                                              attrs["email"], token),
                            query=split.query, fragment=split.fragment)

        plaintext = render_template("mail_password_recovery.txt",
                                    plateform=conf.app.url,
                                    landing_url=urlunsplit(split))
        emails.send(to=attrs["email"], bcc=conf.notification.email,
                    subject="[jarr] Password renew", plaintext=plaintext)
        return None, 204

    @staticmethod
    @auth_ns.expect(login_recovery_parser, validate=True)
    @auth_ns.response(204, "Password updated")
    @auth_ns.response(403, "Wrong token")
    @auth_ns.response(404, "Couldn't find your user")
    def put():
        """Sending new password with recovery token."""
        attrs = login_recovery_parser.parse_args()
        user = UserController().get(login=attrs["login"],
                                    email=attrs["email"])
        if (not user.renew_password_token or not attrs["token"]
                or user.renew_password_token != attrs["token"]):
            raise Forbidden()
        result = UserController().update({"id": user.id},
                                         {"renew_password_token": "",
                                          "password": attrs["password"]})
        return None, 204 if result else 403
