import base64
from flask import Blueprint, Response, request
from web.controllers import IconController
from web.lib.view_utils import etag_match

icon_bp = Blueprint('icon', __name__, url_prefix='/icon')


@icon_bp.route('/', methods=['GET'])
@etag_match
def icon():
    ctr = IconController()
    icon = ctr.get(url=request.args['url'])
    if icon.content is None:
        ctr.delete(request.args['url'])
        content = ''
    else:
        content = icon.content

    headers = {'Cache-Control': 'max-age=86400',
               'Content-Type': icon.mimetype}
    return Response(base64.b64decode(content), headers=headers)
