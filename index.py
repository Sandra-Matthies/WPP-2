class IndexTerm:
    def __init__(self, term, doc_id):
        self.term = term
        self.doc_id = doc_id

    def __eq__(self, other):
        return self.term == other.term and self.doc_id == other.doc_id

    def __hash__(self):
        return hash((self.term, self.doc_id))

    def __repr__(self):
        return f"{self.term}#{self.doc_id}"


class IndexBuilder:
    def __init__(self):
        self._index = {}

    def add(self, term):
        self._index[term] = self._index.get(term, 0) + 1

    def build(self):
        # Sort by term, then docID, then count.
        self._index = sorted(
            self._index.items(), key=lambda k: (k[0].term, k[0].doc_id, -k[1])
        )
        return Index(self._index)


class Index:
    def __init__(self, index):
        self._index = index