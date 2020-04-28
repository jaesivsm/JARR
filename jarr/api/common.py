import logging
from enum import Enum
from urllib.parse import SplitResult, urlsplit, urlunsplit

from flask_restx import fields

from jarr.bootstrap import conf

logger = logging.getLogger(__name__)

MODEL_PARSER_MAPPING = {bool: fields.Boolean, float: fields.Float,
                        str: fields.String, int: fields.Integer}


class EnumField(fields.String):

    def __init__(self, enum, **kwargs):
        super().__init__(enum=[e.value for e in enum], **kwargs)

    def format(self, value):
        return super().format(getattr(value, 'value', value))


def set_model_n_parser(model, parser, name, type_, **kwargs):
    if isinstance(type_, Enum.__class__):
        model[name] = EnumField(type_, **kwargs)
        kwargs['choices'] = list(type_)
    else:
        model[name] = MODEL_PARSER_MAPPING[type_](**kwargs)
    parser.add_argument(name, type=type_, **kwargs,
                        help=kwargs.pop('description', None))


def parse_meaningful_params(parser):
    nullable_keys = {arg.name for arg in parser.args if arg.nullable}
    return {key: value for key, value in parser.parse_args().items()
            if value is not None or key in nullable_keys}


def get_ui_url(path_extention):
    split = urlsplit(conf.app.url)
    split = SplitResult(scheme=split.scheme,
                        netloc=split.netloc,
                        path=split.path + path_extention,
                        query=split.query, fragment=split.fragment)
    return urlunsplit(split)
