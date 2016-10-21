from flask import current_app
from flask_restful import Api

from bootstrap import conf
from web.controllers.category import CategoryController
from web.views.api.common import (PyAggResourceExisting, PyAggResourceMulti,
                                  PyAggResourceNew)


class CategoryNewAPI(PyAggResourceNew):
    controller_cls = CategoryController


class CategoryAPI(PyAggResourceExisting):
    controller_cls = CategoryController


class CategoriesAPI(PyAggResourceMulti):
    controller_cls = CategoryController


api = Api(current_app, prefix=conf.API_ROOT)
api.add_resource(CategoryNewAPI, '/category', endpoint='category_new.json')
api.add_resource(CategoryAPI, '/category/<int:obj_id>',
                 endpoint='category.json')
api.add_resource(CategoriesAPI, '/categories', endpoint='categories.json')
