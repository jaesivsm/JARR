from flask_restful import Api
from flask_login import current_user

from jarr.bootstrap import conf
from jarr.controllers.category import CategoryController
from jarr.views.api.common import (PyAggResourceExisting, PyAggResourceMulti,
                                  PyAggResourceNew)


class CategoryNewAPI(PyAggResourceNew):
    controller_cls = CategoryController

    def post(self):
        """overriden cause you can create categories as normal user"""
        attrs = self.reqparse_args(right='write')
        if not attrs.get('user_id'):
            attrs['user_id'] = current_user.id
        return self.controller.create(**attrs), 201


class CategoryAPI(PyAggResourceExisting):
    controller_cls = CategoryController


class CategoriesAPI(PyAggResourceMulti):
    controller_cls = CategoryController


def load(application):
    api = Api(application, prefix=conf.api_root)
    api.add_resource(CategoryNewAPI, '/category', endpoint='category_new.json')
    api.add_resource(CategoryAPI, '/category/<int:obj_id>',
                     endpoint='category.json')
    api.add_resource(CategoriesAPI, '/categories', endpoint='categories.json')
