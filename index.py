from Levenshtein import distance as lev


class IndexTerm:
    def __init__(self, term, doc_id, pos):
        self.term = term
        self.doc_id = doc_id
        self.position = pos
        self.kgrams = []

    def __eq__(self, other):
        return (
            self.term == other.term
            and self.doc_id == other.doc_id
            and self.position == other.position
            and self.kgrams == other.kgrams
        )

    def __hash__(self):
        return hash((self.term, self.doc_id, self.position, tuple(self.kgrams)))

    def __repr__(self):
        return f"{self.term}#{self.doc_id}#{self.kgrams}"


class PostingList:
    def __init__(self, doc_id: str, positions: list[int]):
        self.doc_id = doc_id
        self.positions = positions

    def __repr__(self):
        return f"{self.doc_id}:{self.positions}"


class PostingItem:
    def __init__(self, term: str, doc_freq: int, postings: list[PostingList]):
        self.term = term
        self.doc_freq = doc_freq
        self.postings = postings

    def __repr__(self):
        return f"{self.term}:{self.doc_freq} = {self.postings}"


class IndexBuilder:
    def __init__(self):
        self._index = {}

    def add(self, term: IndexTerm):
        self._index[term] = self._index.get(term, 0) + 1

    def build(self):
        # Mapping from (term.term, term.doc_id) to a list of positions.
        positions_map = {}
        for term in self._index.keys():
            positions_map[(term.term, term.doc_id)] = positions_map.get(
                (term.term, term.doc_id), []
            ) + [term.position]

        # Sort by term, then docID, then count.
        sorted_index = sorted(
            self._index.items(), key=lambda k: (k[0].term, k[0].doc_id, -k[1])
        )

        posting_items = {}

        for term, doc_id in sorted_index:
            positions = positions_map[(term.term, term.doc_id)]
            if term.term not in posting_items:
                posting_items[term.term] = PostingItem(
                    term.term,
                    1,
                    [PostingList(doc_id, positions)],
                )
            else:
                posting_items[term.term].doc_freq += 1
                posting_items[term.term].postings.append(PostingList(doc_id, positions))

        # TODO: posting_items contains duplicate positions.
        print(posting_items["in"])

        return Index(posting_items)


class Index:
    def __init__(self, entries: dict[str, PostingItem]):
        self._index = entries

    def get_posting_list(self, term) -> PostingList:
        return self._index[term].postings if term in self._index else None


# Klasse für die KGramm Index
# Für eine Abfrage, die nicht mindestens r Dokumente zurück liefert wird eine Rechtschreibkorrektur durchgeführt.
# Für einen Anfrageterm t wird ein k-gramm Index erstellt, der alle k-gramme von t enthält.
# Für jedes k-gramm wird eine potentzieller Wert im Index gepeichert -> t'
# Für jeden Term t' im Index wird die Levenshtein Distanz zwischen t und t' berechnet und gespeichert.
# Die Ergebnisliste wird nach der Levenshtein Distanz sortiert.
class KGramIndex:
    def __init__(self, term):
        self._term = term
        self._kgrams = []

    # Erstellung k-gramme
    def build(self, n):
        for i in range(0, len(self._term) - 1):
            kgram = self._term[i : i + n]
            if kgram not in self._kgrams and len(kgram) == n:
                self._kgrams.append({"k": kgram, "values": []})

    def setKGramValues(self, termList):
        for val in range(0, len(termList) - 1):
            idx = 0
            for k in self._kgrams:
                if k in val:
                    if val not in self._kgrams[idx]["values"]:
                        self._kgrams[idx]["values"].append(
                            {"val": val, "lDist": self.computeLevenstheinDistance(val)}
                        )
                idx += 1
            self.orderByLevenstheinDistance()

    def computeLevenstheinDistance(self, value):
        return lev(self._term, value)

    def orderByLevenstheinDistance(self):
        for i in range(0, len(self._kgrams) - 1):
            self._kgrams[i]["values"].sort(key=lambda x: x["lDist"])
