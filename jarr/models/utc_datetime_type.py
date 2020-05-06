from sqlalchemy import types
from datetime import datetime, timezone


class UTCDateTime(types.TypeDecorator):
    impl = types.DateTime
    python_type = datetime

    @staticmethod
    def process_bind_param(value, dialect):
        if value is not None:
            if not value.tzinfo:
                value = value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    @staticmethod
    def process_result_value(value, dialect):
        if value is not None:
            if value.tzinfo:
                raise ValueError("%r tzinfo is defined, shouldn't be")
            return value.replace(tzinfo=timezone.utc)
        return value

    @staticmethod
    def process_literal_param(value, dialect):
        raise NotImplementedError("can't process %r for %r" % (value, dialect))
