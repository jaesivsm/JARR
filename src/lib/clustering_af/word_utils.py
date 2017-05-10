from functools import wraps
import logging

from .extra_stopwords import extra_stopwords

logger = logging.getLogger(__name__)


class FakeStemmer():
    """
    If nltk is not installed, no stemming
    """
    def stem(self, txt):
        return txt


def nltk_lang(func):
    # from iso-639-1 to NLTK language definition
    @wraps(func)
    def inner(lang):
        iso_to_nltk = {
                'de': 'german',
                'en': 'english',
                'es': 'spanish',
                'fr': 'french',
        }
        if lang:
            for iso_lang in iso_to_nltk:
                if lang.startswith(iso_lang):
                    lang = iso_to_nltk[iso_lang]
                    break
        return func(lang or '')
    return inner


@nltk_lang
def get_stemmer(lang):
    try:
        from nltk import SnowballStemmer
        return SnowballStemmer(lang)
    except Exception:
        return FakeStemmer()


@nltk_lang
def get_stopwords(lang):
    stopwords = extra_stopwords.get(lang, set())
    try:
        from nltk.corpus import stopwords as nltk_stopwords
        return set(nltk_stopwords.words(lang)) | stopwords
    except Exception:
        return stopwords
