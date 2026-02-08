import base64

from sqlalchemy.exc import IntegrityError

from jarr.bootstrap import session
from jarr.lib.utils import jarr_get
from jarr.models import Icon

from .abstract import AbstractController


class IconController(AbstractController):
    _db_cls = Icon
    _user_id_key = None  # type: str

    @staticmethod
    def _build_from_url(attrs):
        if "url" in attrs and "content" not in attrs:
            try:
                resp = jarr_get(attrs["url"])
                attrs["url"] = resp.url
                attrs["mimetype"] = resp.headers.get("content-type", None)
                attrs["content"] = base64.b64encode(resp.content).decode(
                    "utf8"
                )
            except Exception:
                return attrs
        return attrs

    def create(self, **attrs):
        attrs = self._build_from_url(attrs)
        try:
            return super().create(**attrs)
        except IntegrityError:
            # Icon already exists, rollback and return existing icon
            session.rollback()
            # Query for existing icon - need to check if it actually exists
            existing = self.read(url=attrs["url"]).first()
            if existing:
                return existing
            # If icon still doesn't exist after rollback, re-raise
            raise

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
