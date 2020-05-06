from flask import make_response, render_template, request
from flask_jwt import current_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import UnprocessableEntity

import opml
from jarr.controllers import CategoryController, FeedController, UserController
from jarr.lib.utils import utc_now

opml_ns = Namespace('opml',
        description="Allows to export and import OPML files")
model = opml_ns.model('OPML result', {
        'created': fields.Integer(),
        'failed': fields.Integer(),
        'existing': fields.Integer(),
        'exceptions': fields.List(fields.String())})
parser = opml_ns.parser()
parser.add_argument('opml_file', type=FileStorage, required=True)

OK_GET_HEADERS = {'Content-Type': 'application/xml',
                  'Content-Disposition': 'attachment; filename=feeds.opml'}


@opml_ns.route('')
class OPMLResource(Resource):

    @staticmethod
    @opml_ns.response(200, 'OK', headers=OK_GET_HEADERS)
    @jwt_required()
    def get():
        user_id = current_identity.id
        user = UserController(user_id).get(id=user_id)
        categories = {cat.id: cat
                      for cat in CategoryController(user_id).read()}
        response = make_response(render_template('opml.xml', user=user,
                categories=categories, feeds=FeedController(user_id).read(),
                now=utc_now()))
        for key, value in OK_GET_HEADERS.items():
            response.headers[key] = value
        return response

    @staticmethod
    @opml_ns.expect(parser, validate=True)
    @opml_ns.response(201, 'Feed were created from OPML file', model=model)
    @opml_ns.response(200, 'No error and no feed created', model=model)
    @opml_ns.response(400, "Exception while creating fields", model=model)
    @opml_ns.response(422, "Couldn't parse OPML file")
    @jwt_required()
    def post():
        opml_file = request.files['opml_file']

        try:
            subscriptions = opml.from_string(opml_file.read())
        except Exception as error:
            raise UnprocessableEntity("Couldn't parse OPML file (%r)" % error)

        ccontr = CategoryController(current_identity.id)
        fcontr = FeedController(current_identity.id)
        counts = {'created': 0, 'existing': 0, 'failed': 0, 'exceptions': []}
        categories = {cat.name: cat.id for cat in ccontr.read()}
        for line in subscriptions:
            try:
                link = line.xmlUrl
            except Exception as error:
                counts['failed'] += 1
                counts['exceptions'].append(str(error))
                continue

            # don't import twice
            if fcontr.read(link=link).count():
                counts['existing'] += 1
                continue

            # handling categories
            cat_id = None
            category = getattr(line, 'category', '').lstrip('/')
            if category:
                if category not in categories:
                    new_category = ccontr.create(name=category)
                    categories[new_category.name] = new_category.id
                cat_id = categories[category]

            fcontr.create(title=getattr(line, 'text', None),
                          category_id=cat_id,
                          description=getattr(line, 'description', None),
                          link=link,
                          site_link=getattr(line, 'htmlUrl', None))
            counts['created'] += 1
        code = 200
        if counts.get('created'):
            code = 201
        elif counts.get('failed'):
            code = 400
        return counts, code
