"""
Group articles that talks about the same subject.
If two articles, in the same category, have enough similar tokens, we assume
that they talk about the same subject, and we group them in a meta-article
"""
from collections import OrderedDict
from jarr.lib.clustering_af.vector import TFIDFVector
from jarr.models.article import Article


def get_cosine_similarity(left_vector: TFIDFVector,
                          article: Article,
                          term_frequencies: OrderedDict,
                          corpus_size: int) -> float:
    """
    For a given vector and an article will return their cosine similarity.

    Parameter
    ---------
    left_vector: lib.clustering_ad.vector.SparseVector
        the vector of the main article
    article: models.article.Article
    frequencies: dict
        key = term in the corpus, value = number of document with that term
    corpus_size: int
        the total number of documents in the sample

    """
    right_vector = article.get_tfidf_vector(term_frequencies, corpus_size)
    norms = left_vector.norm * right_vector.norm
    if not norms:
        return 0
    return (left_vector * right_vector) / norms


def get_terms_frequencies(*articles):
    """
    Parameter
    ---------
    articles: models.article objects

    Return
    ------
    dictionnary: {token: number of documents containing tokens}
    """
    frequencies = OrderedDict()
    for article in articles:
        for term in article.simple_vector:
            if term in frequencies:
                frequencies[term] += 1
            else:
                frequencies[term] = 1
    return frequencies


def get_best_match_and_score(article, neighbors):
    corpus_size = 1 + len(neighbors)  # current article + neighbors
    term_frequencies = get_terms_frequencies(article, *neighbors)
    vector = article.get_tfidf_vector(term_frequencies, corpus_size,
                                      will_be_left_member=True)
    rank = {get_cosine_similarity(vector, neighbor,
                                  term_frequencies, corpus_size): neighbor
            for neighbor in neighbors}
    return rank[max(rank)], max(rank)
