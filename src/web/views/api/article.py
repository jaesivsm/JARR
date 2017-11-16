import logging
from datetime import datetime

import dateutil.parser
from flask_restful import Api

from bootstrap import conf
from web.controllers import ArticleController
from web.views.api.common import (PyAggAbstractResource, PyAggResourceExisting,
                                  PyAggResourceMulti, PyAggResourceNew)
from web.views.common import api_permission

logger = logging.getLogger(__name__)


class ArticleNewAPI(PyAggResourceNew):
    controller_cls = ArticleController


class ArticleAPI(PyAggResourceExisting):
    controller_cls = ArticleController


class ArticlesAPI(PyAggResourceMulti):
    controller_cls = ArticleController


class ArticlesChallenge(PyAggAbstractResource):
    controller_cls = ArticleController
    attrs = {'ids': {'action': 'append', 'type': dict, 'default': []}}

    @api_permission.require(http_exception=403)
    def get(self):
        parsed_args = self.reqparse_args(right='read')
        # collecting all attrs for casting purpose
        attrs = self.controller_cls._get_attrs_desc('admin')
        for id_dict in parsed_args['ids']:
            keys_to_ignore = []
            for key in id_dict:
                if key not in attrs:
                    logger.warning("got %s:%r which is gonna be ignored",
                                   key, id_dict.get(key))
                    keys_to_ignore.append(key)
                    continue
                if issubclass(attrs[key]['type'], datetime):
                    id_dict[key] = dateutil.parser.parse(id_dict[key])
            for key in keys_to_ignore:
                del id_dict[key]

        result = list(self.controller.challenge(parsed_args['ids']))
        return result or None, 200 if result else 204


def load(application):
    api = Api(application, prefix=conf.API_ROOT)
    api.add_resource(ArticleNewAPI, '/article', endpoint='article_new.json')
    api.add_resource(ArticleAPI, '/article/<int:obj_id>',
                     endpoint='article.json')
    api.add_resource(ArticlesAPI, '/articles', endpoint='articles.json')
    api.add_resource(ArticlesChallenge, '/articles/challenge',
                     endpoint='articles_challenge.json')
