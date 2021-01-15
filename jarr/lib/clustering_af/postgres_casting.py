from bs4 import BeautifulSoup
from sqlalchemy import func
from jarr.bootstrap import conf


LANG_TO_PSQL_MAPPING = {'da': 'danish',
                        'nl': 'dutch',
                        'du': 'dutch',
                        'en': 'english',
                        'uk': 'english',
                        'us': 'english',
                        'fi': 'finnish',
                        'fr': 'french',
                        'de': 'german',
                        'ge': 'german',
                        'hu': 'hungarian',
                        'it': 'italian',
                        'no': 'norwegian',
                        'pt': 'portuguese',
                        'po': 'portuguese',
                        'ro': 'romanian',
                        'ru': 'russian',
                        'es': 'spanish',
                        'sv': 'swedish',
                        'sw': 'swedish',
                        'ts': 'turkish',
                        'tk': 'turkish',
                        'tw': 'turkish',
                        'tr': 'turkish'}


def get_postgres_lang(lang):
    return LANG_TO_PSQL_MAPPING.get((lang or '').lower()[:2],
                                    conf.clustering.tfidf.default_lang)


def to_vector(extract=None, parsed=None):
    if not extract and not parsed:
        return
    title, tags, content, lang = None, None, None, None
    if parsed:
        title, tags = parsed.title, ' '.join(parsed.tags)
        content = parsed.cleaned_text
        lang = get_postgres_lang(parsed.meta_lang)
    if extract:
        title = extract.get('title')
        tags = ' '.join(extract.get('tags') or [])
        lang = get_postgres_lang(extract.get('lang'))
        if not content and extract.get('content'):
            content = BeautifulSoup(extract['content'], 'html.parser').text
    statement = None
    for value, weight in (title, 'A'), (content, 'B'), (tags, 'C'):
        if not value:
            continue
        vector = func.setweight(func.to_tsvector(lang, value), weight)
        if statement is None:
            statement = vector
        else:
            statement = statement.op('||')(vector)
    return statement
