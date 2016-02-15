from datetime import datetime
from flask import current_app
from flask.ext.login import login_user
from flask.ext.principal import (Identity, Permission, RoleNeed,
                                 session_identity_loader, identity_changed)
from web.controllers import UserController

admin_role = RoleNeed('admin')
api_role = RoleNeed('api')

admin_permission = Permission(admin_role)


def login_user_bundle(user):
    login_user(user)
    identity_changed.send(current_app, identity=Identity(user.id))
    session_identity_loader()
    UserController(user.id).update(
                {'id': user.id}, {'last_connection': datetime.utcnow()})
