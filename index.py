
from Levenshtein import distance as lev

class IndexTerm:
    def __init__(self, term, doc_id):
        self.term = term
        self.doc_id = doc_id
        self.kgrams = []

    def __eq__(self, other):
        return self.term == other.term and self.doc_id == other.doc_id

    def __hash__(self):
        return hash((self.term, self.doc_id))

    def __repr__(self):
        return f"{self.term}#{self.doc_id}#{self.kgrams}"


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
        for i in range(0, len(self._term)-1):
            kgram = self._term[i : i + n]
            if kgram not in self._kgrams and len(kgram) == n:
                self._kgrams.append({"k":kgram, "values":[]})

    def setKGramValues(self, termList):
        for val in range(0, len(termList)-1):
            idx = 0
            for k in self._kgrams:
                if(k in val):
                    if(val not in self._kgrams[idx]["values"]):
                        self._kgrams[idx]["values"].append({"val": val, "lDist": self.computeLevenstheinDistance(val)})
                idx += 1
            self.orderByLevenstheinDistance()

    def computeLevenstheinDistance(self, value):
        return lev(self._term, value)

    def orderByLevenstheinDistance(self):
        for i in range(0, len(self._kgrams)-1):
            self._kgrams[i]["values"].sort(key=lambda x: x["lDist"])
    
    
    

