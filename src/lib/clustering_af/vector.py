from math import log10, sqrt


class SparseVector:

    def __init__(self, dimensions, will_be_left_member):
        self.dimensions = {i: dim for i, dim in enumerate(dimensions)
                            if dim != 0}
        self.norm = sqrt(sum(pow(v, 2) for v in self.dimensions.values()))
        if will_be_left_member:
            self._common_dims = set(self.dimensions).intersection

    def __mul__(self, other):
        return sum(self.dimensions[k] * other.dimensions[k]
                   for k in self._common_dims(other.dimensions))


class TFIDFVector(SparseVector):

    def __init__(self, doc, freq, tokens, nb_docs, will_be_left_member=False):
        doc_set = set(doc)
        super().__init__((self.get_tfidf_weight(token, doc, freq, nb_docs)
                          if token in doc_set else 0 for token in tokens),
                          will_be_left_member)

    @staticmethod
    def get_tfidf_weight(token, document, frequences, nb_docs):
        return ((document.count(token) / len(document))  # tf
                * log10(nb_docs / (1 + frequences.get(token, 0))))  # idf
