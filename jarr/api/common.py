import logging

from flask_restplus import fields

logger = logging.getLogger(__name__)

MODEL_PARSER_MAPPING = {bool: fields.Boolean, float: fields.Float,
                        str: fields.String, int: fields.Integer}


def set_model_n_parser(model, parser, name, type_, **kwargs):
    model[name] = MODEL_PARSER_MAPPING[type_](**kwargs)
    parser.add_argument(name, type=type_, **kwargs,
            help=kwargs.pop('description', None))


def parse_meaningful_params(parser):
    return {key: value for key, value in parser.parse_args().items()
            if value is not None}
