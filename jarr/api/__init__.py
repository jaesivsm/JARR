import logging
from datetime import timedelta
from functools import lru_cache

from flask import Flask, got_request_exception, request_tearing_down
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_restx import Api
from jarr.bootstrap import commit_pending_sql, conf, rollback_pending_sql
from jarr.controllers import UserController
from jarr.lib.utils import default_handler
from sqlalchemy.exc import IntegrityError


@lru_cache(maxsize=10)
def get_cached_user(user_id):
    return UserController().get(id=user_id)


def setup_jwt(application, api):
    application.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(
        days=conf.auth.refresh_token_expiration_days
    )
    application.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        seconds=conf.auth.expiration_sec
    )
    application.config["JWT_SECRET_KEY"] = conf.auth.secret_key
    jwt = JWTManager(application)

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    @jwt.user_lookup_loader
    def __identity(_jwt_header, jwt_data):
        return get_cached_user(jwt_data["sub"])

    @api.errorhandler(JWTExtendedException)
    def handle_jwt_error(error):
        """Mapping JWT error to Unauthorized."""
        return {
            "error": error.__class__.__name__,
            "message": ", ".join(error.args),
        }, 401

    @api.errorhandler(IntegrityError)
    def handle_sqla_error(error):
        """Mapping IntegrityError to HTTP Conflict(409)."""
        return {"message": "Database rules prevented this operation"}, 409

    return jwt, handle_jwt_error, handle_sqla_error


def setup_api(application):
    authorizations = {
        "apikey": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
        }
    }

    api = Api(
        application,
        version="3.0",
        doc="/",
        security="apikey",
        authorizations=authorizations,
        contact_mail=conf.api.admin_mail,
    )

    from jarr.api import (
        auth,
        category,
        cluster,
        feed,
        metrics,
        oauth,
        one_page_app,
        opml,
        user,
    )

    api.add_namespace(one_page_app.default_ns)
    api.add_namespace(feed.feed_ns)
    api.add_namespace(cluster.cluster_ns)
    api.add_namespace(category.category_ns)
    api.add_namespace(opml.opml_ns)
    api.add_namespace(user.user_ns)
    api.add_namespace(auth.auth_ns)
    api.add_namespace(oauth.oauth_ns)
    api.add_namespace(metrics.metrics_ns)
    return api


def create_app(testing=False):
    application = Flask(
        __name__, static_folder="jarr/static", template_folder="../templates"
    )

    CORS(application, resources={r"/*": {"origins": "*"}})
    if testing:
        application.debug = True
        application.config["TESTING"] = True
        application.config["PRESERVE_CONTEXT_ON_EXCEPTION"] = False
    else:
        application.debug = conf.log.level <= logging.DEBUG
    application.config["PREFERRED_URL_SCHEME"] = conf.api.scheme
    application.config["RESTX_JSON"] = {"default": default_handler}
    if conf.api.server_name:
        application.config["SERVER_NAME"] = conf.api.server_name

    api = setup_api(application)
    setup_jwt(application, api)

    request_tearing_down.connect(commit_pending_sql, application)
    got_request_exception.connect(rollback_pending_sql, application)
    return application
