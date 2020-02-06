import random
from flask import render_template, current_app
from flask_restplus import Namespace, Resource, fields
from werkzeug.exceptions import BadRequest, Forbidden
from jarr.lib import emails
from jarr.bootstrap import conf
from jarr.controllers import UserController

auth_ns = Namespace('auth', description="Auth related operations")
model = auth_ns.model('Login', {
    'access_token': fields.String(description="The token that must be place "
            "in the 'Authorization' header precedeed with 'JWT '"),
})
login_parser = auth_ns.parser()
login_parser.add_argument('login', type=str, required=True)
login_parser.add_argument('password', type=str, required=True)
login_recovery_parser = auth_ns.parser()
login_recovery_parser.add_argument('email', type=str, required=True)
login_recovery_parser.add_argument('token', type=str, required=True)
login_recovery_parser.add_argument('password', type=str, required=True)


@auth_ns.route('')
class LoginResource(Resource):

    @auth_ns.expect(login_parser)
    @auth_ns.response(200, 'OK', model=model)
    @auth_ns.response(400, 'Missing params')
    @auth_ns.response(403, 'Forbidden')
    def post(self):
        "Given valid credentials, will provide a token to request the API"
        attrs = login_parser.parse_args()
        jwt = current_app.extensions['jwt']
        user = jwt.authentication_callback(attrs['login'], attrs['password'])
        if not user:
            raise Forbidden()
        access_token = jwt.jwt_encode_callback(user)
        return {'access_token': access_token.decode('utf8')}, 200


@auth_ns.route('_recovery/<email>')
class InitPasswordRecovery(Resource):

    @auth_ns.response(204, 'Token generated and mail sent')
    @auth_ns.response(400, 'Bad request')
    def post(self, email):
        """Initialize password recovery by creating a uniq token and sending
        a mail with link to password recovery page"""
        token = str(random.getrandbits(128))
        changed = UserController().update(
                {'email': email}, {'renew_password_token': token})
        if not changed:
            raise BadRequest("No user with %r was found" % email)
        plaintext = render_template('mail_password_recovery.txt',
                plateform=conf.platform_url, email=email, token=token)
        emails.send(to=email, bcc=conf.notification.email,
                    subject="[jarr] Password renew", plaintext=plaintext)
        return None, 204


@auth_ns.route('_recovery')
class PasswordRecovery(Resource):

    @auth_ns.expect(login_recovery_parser, validate=True)
    @auth_ns.response(204, "Password updated")
    @auth_ns.response(403, "Wrong token")
    @auth_ns.response(404, "Email doesn't match any user")
    def put(self):
        """Sending new password with recovery token"""
        attrs = login_recovery_parser.parse_args()
        user = UserController().get(email=attrs['email'])
        if user.renew_password_token != attrs['token']:
            raise Forbidden("No right to update password for this user")

        user = UserController().update({'id': user.id},
                {'renew_password_token': '', 'password': attrs['password']})
        return None, 204
