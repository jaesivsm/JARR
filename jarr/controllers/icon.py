import base64
import logging

from sqlalchemy.exc import IntegrityError

from jarr.bootstrap import session
from jarr.lib.utils import jarr_get
from jarr.models import Icon

from .abstract import AbstractController

logger = logging.getLogger(__name__)


class IconController(AbstractController):
    _db_cls = Icon
    _user_id_key = None  # type: str

    @staticmethod
    def _build_from_url(attrs):
        url = attrs.get("url")
        if "url" in attrs and "content" not in attrs:
            logger.info("IconController: fetching icon from %s", url)
            try:
                resp = jarr_get(attrs["url"])
                attrs["url"] = resp.url
                attrs["mimetype"] = resp.headers.get("content-type", None)
                attrs["content"] = base64.b64encode(resp.content).decode(
                    "utf8"
                )
                logger.info(
                    "IconController: successfully fetched icon from %s", url
                )
            except Exception as error:
                logger.error(
                    "IconController: failed to fetch icon from %s: %s",
                    url,
                    error,
                    exc_info=True,
                )
                return attrs
        return attrs

    def create(self, **attrs):
        logger.info(
            "IconController.create: creating icon %s", attrs.get("url")
        )
        attrs = self._build_from_url(attrs)
        try:
            result = super().create(**attrs)
            logger.info(
                "IconController.create: icon created and committed %s",
                attrs.get("url"),
            )
            return result
        except IntegrityError as error:
            # Icon already exists, rollback and return existing icon
            logger.warning(
                "IconController.create: IntegrityError for %s: %s",
                attrs.get("url"),
                error,
            )
            session.rollback()
            # Query for existing icon - need to check if it actually exists
            existing = self.read(url=attrs["url"]).first()
            if existing:
                logger.info(
                    "IconController.create: returning existing icon %s",
                    attrs.get("url"),
                )
                return existing
            # If icon still doesn't exist after rollback,
            # Re-raise the error
            logger.error(
                "IconController.create: icon doesn't exist after rollback"
            )
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
