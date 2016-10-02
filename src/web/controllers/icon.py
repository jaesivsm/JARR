import base64
from bootstrap import db
from lib.utils import jarr_get
from web.models import Icon
from .abstract import AbstractController


class IconController(AbstractController):
    _db_cls = Icon
    _user_id_key = None

    def _build_from_url(self, attrs):
        if 'url' in attrs and 'content' not in attrs:
            try:
                resp = jarr_get(attrs['url'])
            except Exception:
                return attrs
            attrs.update({'url': resp.url,
                    'mimetype': resp.headers.get('content-type', None),
                    'content': base64.b64encode(resp.content).decode('utf8')})
        return attrs

    def create(self, **attrs):
        return super().create(**self._build_from_url(attrs))

    def update(self, filters, attrs):
        attrs = self._build_from_url(attrs)
        return super().update(filters, attrs, *args, **kwargs)

    def delete(self, url):
        obj = self.get(url=url)
        db.session.delete(obj)
        db.session.commit()
        return obj
