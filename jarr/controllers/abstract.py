import logging
from datetime import datetime, timezone

import dateutil.parser
from sqlalchemy import and_, or_
from sqlalchemy.ext.associationproxy import AssociationProxy
from werkzeug.exceptions import Forbidden, NotFound

from jarr_common.utils import utc_now
from jarr.bootstrap import session

logger = logging.getLogger(__name__)


def cast_to_utc(dt_obj):
    dt_obj = dateutil.parser.parse(dt_obj)
    if not dt_obj.tzinfo:
        return dt_obj.replace(tzinfo=timezone.utc)
    return dt_obj


class AbstractController:
    _db_cls = None  # reference to the database class
    _user_id_key = 'user_id'

    def __init__(self, user_id=None, ignore_context=False):
        """User id is a right management mechanism that should be used to
        filter objects in database on their denormalized "user_id" field
        (or "id" field for users).
        Should no user_id be provided, the Controller won't apply any filter
        allowing for a kind of "super user" mode.
        """
        try:
            self.user_id = int(user_id)
        except TypeError:
            self.user_id = user_id

    @staticmethod
    def _to_comparison(key, model):
        "extract from the key the method used by sqla for comparison"
        if '__' not in key:
            return getattr(model, key).__eq__
        attr, ope = key.rsplit('__', 1)
        if ope == 'in':
            return getattr(model, attr).in_
        elif ope not in {'like', 'ilike'}:
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
            else:
                db_filters.add(cls._to_comparison(key, cls._db_cls)(value))
        return db_filters

    def _get(self, **filters):
        """ Will add the current user id if that one is not none (in which case
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
            raise Forbidden({'message': 'No authorized to access %r (%r)'
                                % (self._db_cls.__class__.__name__, filters)})
        if not obj:
            raise NotFound({'message': 'No %r (%r)'
                                % (self._db_cls.__class__.__name__, filters)})
        return obj

    def create(self, **attrs):
        assert self._db_cls is not None
        assert attrs, "attributes to update must not be empty"
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
        assert attrs, "attributes to update must not be empty"
        result = self._get(**filters).update(attrs, synchronize_session=False)
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

    @classmethod
    def _extra_columns(cls, role, right=None):
        return {}

    @classmethod
    def _get_columns(cls, role, right):
        if role == 'admin':
            return set(cls._db_cls.__table__.columns.keys())\
                    .union(cls._db_cls.fields_base_read())\
                    .union(cls._db_cls.fields_base_write())\
                    .union(cls._db_cls.fields_api_read())\
                    .union(cls._db_cls.fields_api_write())
        assert role in {'base', 'api'}, 'unknown role %r' % role
        assert right in {'read', 'write'}, \
                "right must be 'read' or 'write' with role %r" % role
        return getattr(cls._db_cls, 'fields_%s_%s' % (role, right))()

    @classmethod
    def _db_col_to_dict(cls, db_col):
        if db_col.name in getattr(cls._db_cls, 'custom_api_types', {}):
            return cls._db_cls.custom_api_types[db_col.name]
        dict_col = {'type': db_col.type.python_type}
        if issubclass(dict_col['type'], datetime):
            dict_col['default'] = utc_now()
            dict_col['type'] = cast_to_utc
        elif db_col.default:
            dict_col['default'] = db_col.default.arg
        if callable(dict_col.get('default')):
            dict_col['default'] = dict_col['default'](None)
        return dict_col

    @classmethod
    def _get_attrs_desc(cls, role, right=None):
        result = {}
        for column in cls._get_columns(role, right):
            if isinstance(getattr(cls._db_cls, column), AssociationProxy):
                result[column] = {'default': [], 'action': 'append'}
                continue
            try:
                db_col = getattr(cls._db_cls, column).property.columns[0]
            except AttributeError:
                continue
            result[column] = cls._db_col_to_dict(db_col)
        result.update(cls._extra_columns(role, right))
        return result
