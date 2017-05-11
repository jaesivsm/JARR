"""
Group articles that talks about the same subject.
If two articles, in the same category, have enough similar tokens, we assume
that they talk about the same subject, and we group them in a meta-article
"""
import json
from math import log10, sqrt
from collections import Counter


def get_tfidf_weight(token, document, frequences, nb_docs):
    return ((document.count(token) / len(document))  # tf
            * log10(nb_docs / (1 + frequences.get(token, 0))))  # idf


def get_vector(document, frequences, tokens, nb_docs):
    return tuple(get_tfidf_weight(token, document, frequences, nb_docs)
                 for token in tokens)


def get_norm(vector):
    return sqrt(sum(pow(dim, 2) for dim in vector))


def get_similarity_score(art1_vector, art1_norm,
                         article2, frequences, tokens, nb_docs):
    art2_vector = get_vector(article2.valuable_tokens,
                             frequences, tokens, nb_docs)
    scalar_product = sum(p * q for p, q in zip(art1_vector, art2_vector))
    return scalar_product / (art1_norm * get_norm(art2_vector))


def get_token_occurences_count(*articles):
    """
    Parameter
    ---------
    articles: models.article objects

    Return
    ------
    dictionnary: {token: number of documents containing tokens}
    """
    frequences = Counter()
    tokens = set()
    art_vt_sets = []
    for article in articles:
        art_vt_sets.append(set(article.valuable_tokens))
        tokens = tokens.union(art_vt_sets[-1])
    for token in tokens:
        for art_vt_set in art_vt_sets:
            if token in art_vt_set:
                frequences[token] = +1
    return sorted(frequences), frequences


def get_best_match_and_score(article, neighbors):
    nb_docs = len(neighbors)
    tokens, freq = get_token_occurences_count(article, *neighbors)
    article_vector = get_vector(article.valuable_tokens,
                                freq, tokens, nb_docs)
    article_norm = get_norm(article_vector)
    rank = {get_similarity_score(article_vector, article_norm,
                                 neigh, freq, tokens, nb_docs): neigh
            for neigh in neighbors}
    return rank[max(rank)], max(rank)
