from functools import wraps
import logging

from bs4 import BeautifulSoup

from .extra_stopwords import extra_stopwords

logger = logging.getLogger(__name__)

CHARS_TO_STRIP = '.,?!:/[]-_"\'()#@*><'


class FakeStemmer():
    "If nltk is not installed, no stemming"
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


def browse_token(tokens, stemmer, stopwords, lang, resplit=False):
    """For a given list of tokens, will yield every token in it stemmed.
    If token contains '-' or '_' they're gonna be split on that.

    Parameters
    ----------
    tokens: iterable, the tokens to browse
    stemmer: object, a instance of a stemmer, must implement stem()
    stopwords: an iterable, the tokens to be excluded
    resplit: bool, set to true to split on every token

    Yield
    -----
    str, tokens
    """
    for token in tokens:
        if resplit:
            yield from browse_token(token.split(), stemmer, stopwords, lang)
        else:
            token = stemmer.stem(token.strip(CHARS_TO_STRIP).lower())
            # special french handling for "d'" and "l'" and what not
            if lang and lang.startswith('fr') \
                    and len(token) > 2 and token[1] == "'":
                token = stemmer.stem(token[2:])
            if token.isalnum() and token not in stopwords:
                yield token
            elif '-' in token:
                yield from browse_token(token.split('-'),
                        stemmer, stopwords, lang)
            elif '_' in token:
                yield from browse_token(token.split('_'),
                        stemmer, stopwords, lang)


def extract_valuable_tokens(article):
    """Return every extractable tokens from an article.

    Parameters
    ----------
    article: models.article.Article

    Return
    ------
    list, all the stemmed valuable tokens extractable from the article
    """
    lang = article.get('lang')
    stemmer = get_stemmer(lang)
    stopwords = get_stopwords(lang)
    tokens = [token for token in browse_token(article.get('title', '').split(),
                                              stemmer, stopwords, lang)]
    if article.get('content'):
        soup = BeautifulSoup(article['content'], 'html.parser')
        if soup:
            tokens.extend(browse_token(soup.text.split(),
                                       stemmer, stopwords, lang))
    tokens.extend(browse_token(article.get('tags', []),
                               stemmer, stopwords, lang, True))
    return tokens
