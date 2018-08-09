from math import log10, sqrt


class SparseVector:
    """A implentation of the mathematic vector light on complexity

    For a given vector, will only keep non-zero values and allow scalar product
    with a similar vector
    """

    def __init__(self, dimensions, will_be_left_member):
        """
        Parameters
        ----------
        dimensions: iterable, the vector
        will_be_left_member: bool, set to True if it's gonna be on the left
            side of a scalar product (this optimization saves on calculation if
            the vector is never gonna be on the left side of a scalar product)
        """
        self.dimensions = {i: dim for i, dim in enumerate(dimensions)
                           if dim != 0}
        self.norm = sqrt(sum(pow(v, 2) for v in self.dimensions.values()))
        if will_be_left_member:
            self._common_dims = set(self.dimensions).intersection

    def __mul__(self, other):
        return sum(self.dimensions[k] * other.dimensions[k]
                   for k in self._common_dims(other.dimensions))


class TFIDFVector(SparseVector):
    """The represetation of a document as a vector"""

    def __init__(self, doc, freq, tokens, nb_docs, will_be_left_member=False):
        """
        Parameters
        ----------
        doc: iterable, a list of token
        freq: dict, with {token: number of occurence accross all docs}
        tokens: list, tokens to browse
        nb_docs: int, the total number of documents in the sample
        will_be_left_member: bool, set to True if it's gonna be on the left
            side of a scalar product (this optimization saves on calculation if
            the vector is never gonna be on the left side of a scalar product)
        """
        doc_set = set(doc)
        super().__init__((self.get_tfidf_weight(token, doc, freq, nb_docs)
                          if token in doc_set else 0 for token in tokens),
                          will_be_left_member)

    @staticmethod
    def get_tfidf_weight(token, document, frequences, nb_docs):
        """Return the given token weight for the document in the space

        Parameters
        ----------
        token: str, a token
        document: list, the tokens
        frequences: dict, with {token: number of occurence accross all docs}
        nb_docs: int, the total number of documents in the sample
        """
        return ((document.count(token) / len(document))  # tf
                * log10(nb_docs / (1 + frequences.get(token, 0))))  # idf
