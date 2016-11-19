from sqlalchemy import types
from datetime import datetime, timezone


class UTCDateTime(types.TypeDecorator):
    impl = types.DateTime
    python_type = datetime

    def process_bind_param(self, value, engine):
        if value is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value, engine):
        if value is not None:
            assert not value.tzinfo
            return value.replace(tzinfo=timezone.utc)
        return value
