"""
Group articles that talks about the same subject.
If two articles, in the same category, have enough similar tokens, we assume
that they talk about the same subject, and we group them in a meta-article
"""
import json
from collections import Counter
from lib.clustering_af.vector import TFIDFVector


def get_cosine_similarity(v1, article2, freq, tokens, nb_docs):
    v2 = TFIDFVector(article2.valuable_tokens, freq, tokens, nb_docs)
    return (v1 * v2) / (v1.norm * v2.norm)


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
    vector = TFIDFVector(article.valuable_tokens, freq, tokens, nb_docs,
                         will_be_left_member=True)
    rank = {get_cosine_similarity(vector, neigh, freq, tokens, nb_docs): neigh
            for neigh in neighbors}
    return rank[max(rank)], max(rank)
