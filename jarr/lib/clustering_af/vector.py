from math import log10, sqrt
from functools import lru_cache
from collections import OrderedDict


class SparseVector:
    """
    An implentation of the mathematic vector light on complexity.

    For a given vector, will only keep non-zero values and allow scalar product
    with a similar vector
    """

    def __init__(self, dimensions, will_be_left_member: bool = False):
        """
        Parameters
        ----------
        dimensions: iterable
            the vector
        will_be_left_member: bool
            set to True if it's gonna be on the left side of a scalar product
            (this optimization saves on calculation if the vector is never
            gonna be on the left side of a scalar product)
        """
        dimensions = list(dimensions)
        self.dimensions = {term: weight for term, weight in dimensions
                           if weight != 0}
        self.norm = sqrt(sum(pow(v, 2) for v in self.dimensions.values()))
        if will_be_left_member:
            self._common_dims = set(self.dimensions).intersection

    def __mul__(self, other):
        """Multiply two vectors."""
        return sum(self.dimensions[k] * other.dimensions[k]
                   for k in self._common_dims(other.dimensions))


def get_tfidf_weight(term_document_count: int,
                     document_size: int,
                     term_frequency: int,
                     corpus_size: int):
    """
    Return the given token weight for the document in the space.

    Parameters
    ----------
    term_document_count: int
    document_size: int
    term_frequency: int
    corpus_size: int
    """
    if not term_document_count:
        return 0
    return ((term_document_count / document_size)  # tf
            * log10(corpus_size / (1 + term_frequency)))  # idf


class TFIDFVector(SparseVector):
    """
    The represetation of a document as a vector.
    """

    def __init__(self, document: dict,
                 document_size: int,
                 term_frequencies: OrderedDict,
                 corpus_size: int,
                 will_be_left_member=False):
        """
        Parameters
        ----------
        document: key = term, value = count in the document
        document_size: total count of terms in the document
        term_frequencies:
            {term: number of occurence accross all docs}
        corpus_size: int
            the total number of documents in the sample
        will_be_left_member: bool
            set to True if it's gonna be on the left side of a scalar product
            (this optimization saves on calculation if the vector is never
            gonna be on the left side of a scalar product)
        """
        if corpus_size:
            super().__init__(((term, get_tfidf_weight(document.get(term, 0),
                                                      document_size,
                                                      term_frequencies[term],
                                                      corpus_size))
                               for term in term_frequencies),
                              will_be_left_member)
        else:
            super().__init__((0 for term in term_frequencies),
                             will_be_left_member)


@lru_cache()
def get_simple_vector(vector):
    if vector is None:
        return None, 0
    simple_vector = {}
    size = 0
    for word_n_count in vector.split():
        word_n_count = word_n_count.split(':', 1)
        word = word_n_count[0]
        count = word_n_count[1] if len(word_n_count) > 1 else ''
        word = word[1:-1]
        simple_vector[word] = count.count(',') + 1
        size += simple_vector[word]
    return simple_vector, size
