import logging
from enum import Enum

from flask_restx import fields

logger = logging.getLogger(__name__)

MODEL_PARSER_MAPPING = {bool: fields.Boolean, float: fields.Float,
                        str: fields.String, int: fields.Integer}


class EnumField(fields.String):

    def __init__(self, enum, **kwargs):
        super().__init__(enum=[e.value for e in enum], **kwargs)

    def format(self, value):
        return super().format(value.value)


def set_model_n_parser(model, parser, name, type_, **kwargs):
    if isinstance(type_, Enum.__class__):
        model[name] = EnumField(type_, **kwargs)
        kwargs['choices'] = [en.value for en in type_]
    else:
        model[name] = MODEL_PARSER_MAPPING[type_](**kwargs)
    parser.add_argument(name, type=type_, **kwargs,
                        help=kwargs.pop('description', None))


def parse_meaningful_params(parser):
    return {key: value for key, value in parser.parse_args().items()
            if value is not None}
