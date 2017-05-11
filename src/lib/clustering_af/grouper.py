"""
Group articles that talks about the same subject.
If two articles, in the same category, have enough similar tokens, we assume
that they talk about the same subject, and we group them in a meta-article
"""
import json
from collections import Counter

from .word_utils import get_stemmer, get_stopwords

CHARS_TO_STRIP = '.,?!:/[]-_"\'()#@*><'


def browse_token(tokens, stemmer, stopwords, resplit=False):
    for token in tokens:
        if resplit:
            yield from browse_token(token.split(), stemmer, stopwords)
        else:
            token = stemmer.stem(token.strip(CHARS_TO_STRIP).lower())
            if token.isalnum() and token not in stopwords:
                yield token


def extract_valuable_tokens(article):
    stemmer = get_stemmer(article.get('lang'))
    stopwords = get_stopwords(article.get('lang'))
    tokens = [token for token in browse_token(article.get('title', '').split(),
                                              stemmer, stopwords)]
    tokens.extend(tag for tag in browse_token(article.get('tags', []),
                                              stemmer, stopwords, True))
    return tokens


def get_similarity_score(article_1, article_2, token_occurences, nb_docs):
    """
    Similarity of two documents is the sum of the
    inverse document frequency of all tokens that belong to
    both feeds, divided by the length of both feeds

    Parameter
    ---------
    article_i: model.Article objects
    token_occurences: dictionnary {token: int}
    nb_docs: int

    Return
    ------
    float
    """
    return sum(nb_docs / token_occurences[token]
               for token in article_1.valuable_tokens
               if token in article_2.valuable_tokens)


def get_token_occurences_count(articles):
    """
    Build token occurence count, a.k.a a dictionnary
        token -> number of documents containing token

    Parameter
    ---------
    articles: models.article objects

    Return
    ------
    dictionnary: {token: number of documents containing tokens}
    """
    token_occurences = Counter()
    for article in articles:
        for t in article.valuable_tokens:
            token_occurences[t] += 1
    return token_occurences
