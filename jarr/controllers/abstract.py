import logging
from datetime import timezone

import dateutil.parser
from sqlalchemy import and_, or_
from werkzeug.exceptions import Forbidden, NotFound, Unauthorized

from jarr.bootstrap import Base, session

logger = logging.getLogger(__name__)


def cast_to_utc(dt_obj):
    dt_obj = dateutil.parser.parse(dt_obj)
    if not dt_obj.tzinfo:
        return dt_obj.replace(tzinfo=timezone.utc)
    return dt_obj


class AbstractController:
    _db_cls = Base  # reference to the database class, to redefine in child cls
    _user_id_key = 'user_id'

    def __init__(self, user_id=None, ignore_context=False):
        """
        Base methods for controllers accross JARR.
        User id is a right management mechanism that should be used to
        filter objects in database on their denormalized "user_id" field
        (or "id" field for users).
        Should no user_id be provided, the Controller won't apply any filter
        allowing for a kind of "super user" mode.
        """
        if self._db_cls is None:
            raise NotImplementedError("%r _db_cls isn't overridden" % self)
        try:
            self.user_id = int(user_id)
        except TypeError:
            self.user_id = user_id

    @staticmethod
    def _to_comparison(key, model):
        """Extract from the key the method used by sqla for comparison."""
        if '__' not in key:
            return getattr(model, key).__eq__
        attr, ope = key.rsplit('__', 1)
        if ope == 'nin':
            return getattr(model, attr).notin_
        if ope == 'in':
            return getattr(model, attr).in_
        if ope not in {'like', 'ilike'}:
            ope = '__%s__' % ope
        return getattr(getattr(model, attr), ope)

    @classmethod
    def _to_filters(cls, **filters):
        """
        Will translate filters to sqlalchemy filter.
        This method will also apply user_id restriction if available.

        each parameters of the function is treated as an equality unless the
        name of the parameter ends with either "__gt", "__lt", "__ge", "__le",
        "__ne", "__in", "__like" or "__ilike".
        """
        db_filters = set()
        for key, value in filters.items():
            if key == '__or__':
                db_filters.add(or_(*[and_(*cls._to_filters(**sub_filter))
                                     for sub_filter in value]))
            elif key == '__and__':
                for sub_filter in value:
                    for k, v in sub_filter.items():
                        db_filters.add(cls._to_comparison(k, cls._db_cls)(v))
            else:
                db_filters.add(cls._to_comparison(key, cls._db_cls)(value))
        return db_filters

    def _get(self, **filters):
        """
        Abstract get.
        Will add the current user id if that one is not none (in which case
        the decision has been made in the code that the query shouldn't be user
        dependant) and the user is not an admin and the filters doesn't already
        contains a filter for that user.
        """
        if self._user_id_key is not None and self.user_id \
                and filters.get(self._user_id_key) != self.user_id:
            filters[self._user_id_key] = self.user_id
        return session.query(self._db_cls).filter(*self._to_filters(**filters))

    def get(self, **filters):
        """Will return one single objects corresponding to filters"""
        obj = self._get(**filters).first()

        if obj and not self._has_right_on(obj):
            raise Forbidden('No authorized to access %r (%r)' % (
                                self._db_cls.__class__.__name__, filters))
        if not obj:
            raise NotFound('No %r (%r)' % (self._db_cls.__class__.__name__,
                                           filters))
        return obj

    def create(self, **attrs):
        if not attrs:
            raise ValueError("attributes to update must not be empty")
        if self._user_id_key is not None and self._user_id_key not in attrs:
            attrs[self._user_id_key] = self.user_id
        if not (self._user_id_key is None or self._user_id_key in attrs
                or self.user_id is None):
            raise Unauthorized("You must provide user_id one way or another")

        obj = self._db_cls(**attrs)
        session.add(obj)
        session.flush()
        session.commit()
        return obj

    def read(self, **filters):
        return self._get(**filters)

    def update(self, filters, attrs, return_objs=False, commit=True):
        if not attrs:
            logger.error("nothing to update, doing nothing")
            result, commit = {}, False
        else:
            result = self._get(**filters).update(attrs,
                                                 synchronize_session=False)
        if commit:
            session.flush()
            session.commit()
        if return_objs:
            return self._get(**filters)
        return result

    def delete(self, obj_id, commit=True):
        obj = self.get(id=obj_id)
        session.delete(obj)
        if commit:
            session.flush()
            session.commit()
        return obj

    def _has_right_on(self, obj):
        # user_id == None is like being admin
        if self._user_id_key is None:
            return True
        return self.user_id is None \
                or getattr(obj, self._user_id_key, None) == self.user_id

    def assert_right_ok(self, obj_id):
        if not self.user_id:
            raise ValueError("%r user_id can't be None" % self)
        rows = self.__class__().read(id=obj_id).with_entities(
                getattr(self._db_cls, self._user_id_key)).first()
        if not rows:
            raise NotFound()
        if not rows[0] == self.user_id:
            raise Forbidden()
