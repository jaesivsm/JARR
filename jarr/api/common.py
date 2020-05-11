import logging
from enum import Enum
from urllib.parse import SplitResult, urlsplit, urlunsplit

from flask_restx import fields

from jarr.bootstrap import conf

logger = logging.getLogger(__name__)

MODEL_PARSER_MAPPING = {bool: fields.Boolean, float: fields.Float,
                        str: fields.String, int: fields.Integer}

clustering_options = {
        "cluster_enabled": "will allow article in your feeds and categories to"
                           " to be clusterized",
        "cluster_tfidf_enabled": "will allow article in your feeds and categor"
                                 "ies to be clusterized through document compa"
                                 "rison",
        "cluster_same_category": "will allow article in your feeds and categor"
                                 "ies to be clusterized while beloning to the "
                                 "same category",
        "cluster_same_feed": "will allow article in your feeds and categories "
                             "to be clusterized while beloning to the same "
                             "feed",
        "cluster_wake_up": "will unread cluster when article from that feed "
                           "are added to it",
}


def set_clustering_options(level, model, parser, nullable=True):
    if level == "user":
        suffix = " (article's feed and category clustering settings allows it)"
    elif level == "category":
        suffix = " (article's feed and user clustering settings allows it)"
    elif level == "feed":
        suffix = " (article's category and user clustering settings allows it)"
    for option in clustering_options:
        set_model_n_parser(model, parser, option, bool, nullable=nullable,
                           description=clustering_options[option] + suffix)


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
    parser.add_argument(name, type=type_, **kwargs, store_missing=False,
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
