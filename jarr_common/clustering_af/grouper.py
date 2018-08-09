"""
Group articles that talks about the same subject.
If two articles, in the same category, have enough similar tokens, we assume
that they talk about the same subject, and we group them in a meta-article
"""
from collections import Counter
from jarr_common.clustering_af.vector import TFIDFVector


def get_cosine_similarity(v1, article2, freq, tokens, nb_docs):
    """For a given vector and an article will return their cosine similarity

    Parameter
    ---------
    v1: lib.clustering_ad.vector.SparseVector, the vector of the main article
    article2: models.article.Article
    freq: dict, with {token: number of occurence accross all docs}
    tokens: list, tokens to browse
    nb_docs: int, the total number of documents in the sample

    Return
    ------
    int: the cosine similarity
    """
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
