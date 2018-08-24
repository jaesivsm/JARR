import logging
from functools import lru_cache

from flask import Flask
from flask_jwt import JWT, JWTError
from flask_restplus import Api
from sqlalchemy.exc import IntegrityError
from jarr.bootstrap import conf, session, PARSED_PLATFORM_URL
from jarr.controllers import UserController


def __authenticate(username, password):
    return UserController().check_password(username, password)


@lru_cache(maxsize=10)
def get_cached_user(user_id):
    return UserController().get(id=user_id)


def __identity(payload):
    return get_cached_user(payload['identity'])


def setup_sqla_binding(application):

    @application.teardown_request
    def session_clear(exception=None):
        if exception and session.is_active:
            session.rollback()
    return session_clear


def setup_jwt(application, api):
    application.config['JWT_AUTH_USERNAME_KEY'] = 'login'
    application.config['SECRET_KEY'] = conf.secret_key
    jwt = JWT(application, __authenticate, __identity)

    @api.errorhandler(JWTError)
    def handle_jwt_error(error):
        '''This is a custom error'''
        return error, 401

    @api.errorhandler(IntegrityError)
    def handle_sqla_error(error):
        '''This is a custom error'''
        return {'message': 'Database rules prevented this operation'}, 409
    return jwt, handle_jwt_error, handle_sqla_error


def setup_api(application):
    authorizations = {
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
        }
    }

    api = Api(application, version='3.0', doc='/swagger', security='apikey',
              authorizations=authorizations)

    from jarr.api import (feed, cluster, category, one_page_app, opml,
            user, auth, oauth)

    api.add_namespace(one_page_app.default_ns)
    api.add_namespace(feed.feed_ns)
    api.add_namespace(cluster.cluster_ns)
    api.add_namespace(category.category_ns)
    api.add_namespace(opml.opml_ns)
    api.add_namespace(user.user_ns)
    api.add_namespace(auth.auth_ns)
    api.add_namespace(oauth.oauth_ns)
    return api


def create_app(testing=False):
    application = Flask(__name__,
            static_folder='jarr/static',
            template_folder='../templates')
    application.config.from_object(conf)
    if testing:
        application.debug = True
        application.config['TESTING'] = True
        application.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
    else:
        application.debug = conf.log.level <= logging.DEBUG
    application.config['PLATFORM_URL'] = conf.platform_url
    application.config['SERVER_NAME'] = PARSED_PLATFORM_URL.netloc
    application.config['PREFERRED_URL_SCHEME'] = PARSED_PLATFORM_URL.scheme

    setup_sqla_binding(application)
    api = setup_api(application)
    setup_jwt(application, api)
    return application
