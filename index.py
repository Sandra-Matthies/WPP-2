import math
from typing import Optional

from Levenshtein import distance as lev


class IndexTerm:
    def __init__(self, term: str, doc_id: int, pos: int):
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
        return f"{self.term}#{self.doc_id}#{self.kgrams}\n"


class PositionalPosting:
    def __init__(self, doc_id: int, positions: list[int]):
        self.doc_id = doc_id
        self.positions = positions

    def __repr__(self):
        return f"{self.doc_id}:{self.positions}\n"


class PostingList:
    def __init__(self, term: str, doc_freq: int, postings: list[PositionalPosting]):
        self.term = term
        self.doc_freq = doc_freq
        self.postings = postings
        self.doc_ids: set[int] = set()
        # Mapping from doc_id to term frequency.
        self._term_frequency: dict[int, int] = {}

    def calculate_document_frequency(self):
        self.doc_ids = set([posting.doc_id for posting in self.postings])

    def calculate_term_frequency(self):
        for posting in self.postings:
            self._term_frequency[posting.doc_id] = math.log10(
                len(posting.positions) + 1
            )

    def get_term_frequency(self, doc_id: int) -> float:
        return self._term_frequency.get(doc_id, 0)

    def __repr__(self):
        return f"{self.term}:{self.doc_freq} = {self.postings} \n"


class IndexBuilder:
    def __init__(self):
        self._index: dict[IndexTerm, int] = {}
        # Mapping from doc id to doc length.
        self._doc_lengths: dict[int, int] = {}

    def add(self, term: IndexTerm):
        self._index[term] = self._index.get(term, 0) + 1

    def set_doc_len(self, doc_id: int, length: int):
        self._doc_lengths[doc_id] = length

    def build(self):
        # Mapping from (term.term, term.doc_id) to a list of positions.
        positions_map = {}
        for term in self._index.keys():
            positions_map[(term.term, term.doc_id)] = positions_map.get(
                (term.term, term.doc_id), []
            ) + [term.position]

        # Sort by term, then docID.
        sorted_index = sorted(self._index.keys(), key=lambda k: (k.term, k.doc_id))

        postings_lists: dict[str, PostingList] = {}

        for term in sorted_index:
            if (term.term, term.doc_id) not in positions_map:
                continue

            positions = positions_map[(term.term, term.doc_id)]

            del positions_map[(term.term, term.doc_id)]

            if term.term not in postings_lists:
                postings_lists[term.term] = PostingList(
                    term.term,
                    1,
                    [PositionalPosting(term.doc_id, positions)],
                )
            else:
                postings_lists[term.term].doc_freq += 1
                postings_lists[term.term].postings.append(
                    PositionalPosting(term.doc_id, positions)
                )

        for posting_list in postings_lists.values():
            posting_list.calculate_document_frequency()
            posting_list.calculate_term_frequency()

        return Index(postings_lists, self._doc_lengths)


class Index:
    def __init__(self, entries: dict[str, PostingList], doc_lengths: dict[int, int]):
        self._index = entries
        self.doc_ids = sorted(
            set(
                [
                    postings.doc_id
                    for posting_list in entries.values()
                    for postings in posting_list.postings
                ]
            )
        )
        self.doc_lengths = doc_lengths
        self.avg_doc_length = sum(doc_lengths.values()) / len(doc_lengths)

    def __repr__(self):
        return f"{self._index}\n"

    def get_positional_postings(self, term: str) -> list[PositionalPosting]:
        if term not in self._index:
            return []
        return sorted(self._index[term].postings, key=lambda k: k.doc_id)

    def get_posting_list(self, term: str) -> Optional[PostingList]:
        return self._index.get(term, None)


# Klasse für die KGramm Index
# Für eine Abfrage, die nicht mindestens r Dokumente zurück liefert wird eine Rechtschreibkorrektur durchgeführt.
# Für einen Anfrageterm t wird ein k-gramm Index erstellt, der alle k-gramme von t enthält.
# Für jedes k-gramm wird eine potentzieller Wert im Index gepeichert -> t'
# Für jeden Term t' im Index wird die Levenshtein Distanz zwischen t und t' berechnet und gespeichert.
# Die Ergebnisliste wird nach der Levenshtein Distanz sortiert.
class KGramIndex:
    def __init__(self, term):
        self._term = term
        self._kgrams: list[dict[str, list]] = []

    def __repr__(self):
        return f"{self._term} : [{self._kgrams}]\n"

    # Erstellung k-gramme
    def build(self, n: int):
        for i in range(0, len(self._term) - 1):
            letters = int(i) + int(n)
            kgram = self._term[i:+letters]
            # Überprüfung ob kgramm bereits im Index vorhanden ist
            if ((len([d for d in self._kgrams if kgram in d])) == 0) and (
                len(kgram) == int(n)
            ):
                self._kgrams.append({"k": kgram, "values": []})

    def setKGramValues(self, termList: Index):
        # for val in range(0, len(termList) - 1):
        idx = 0
        for k in self._kgrams:
            possbileValues = [d for d in termList._index if k["k"] in d]
            if len(possbileValues) > 0:
                if possbileValues not in k["values"]:
                    for val in possbileValues:
                        # Abfrage zur Länge des Möglichen Terms
                        if not (len(val) > (len(self._term) + 3)) and not (
                            len(val) < (len(self._term) - 3)
                        ):
                            k["values"].append(
                                {
                                    "val": val,
                                    "lDist": self.computeLevenstheinDistance(val),
                                }
                            )
            idx += 1
        self.orderByLevenstheinDistance()

    def computeLevenstheinDistance(self, value):
        return lev(self._term, value)

    def orderByLevenstheinDistance(self):
        for kgram in self._kgrams:
            kgram["values"] = sorted(kgram["values"], key=lambda x: x["lDist"])

    def getKGramsWithLowestLDistValue(self):
        for kgram in self._kgrams:
            treshhold = 0
            if len(kgram["values"]) > 0:
                treshhold = kgram["values"][0]["lDist"]
                outOfScopes = [d for d in kgram["values"] if d["lDist"] > treshhold]
                for outOfScope in outOfScopes:
                    kgram["values"].remove(outOfScope)
                print(kgram["values"])
