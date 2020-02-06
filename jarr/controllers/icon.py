import base64

from jarr.bootstrap import conf, session
from jarr.models import Icon
from jarr.utils import jarr_get

from .abstract import AbstractController


class IconController(AbstractController):
    _db_cls = Icon
    _user_id_key = None  # type: str

    @staticmethod
    def _build_from_url(attrs):
        if 'url' in attrs and 'content' not in attrs:
            try:
                resp = jarr_get(attrs['url'], timeout=conf.crawler.timeout,
                                user_agent=conf.crawler.user_agent)
            except Exception:
                return attrs
            attrs.update({'url': resp.url,
                    'mimetype': resp.headers.get('content-type', None),
                    'content': base64.b64encode(resp.content).decode('utf8')})
        return attrs

    def create(self, **attrs):
        return super().create(**self._build_from_url(attrs))

    def update(self, filters, attrs, return_objs=False, commit=True):
        attrs = self._build_from_url(attrs)
        return super().update(filters, attrs, return_objs, commit)

    def delete(self, obj_id, commit=True):
        obj = self.get(url=obj_id)
        session.delete(obj)
        if commit:
            session.flush()
            session.commit()
        return obj
