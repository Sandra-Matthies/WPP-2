from index import PositionalPosting


class Posting:
    def __init__(self):
        self._posting = {}

    def __repr__(self) -> str:
        return f"{self._posting}\n"

    @staticmethod
    # Basic Insersect merge two lists of IndexTerm objects and return the result as list
    def intersect(
        list1: list[PositionalPosting], list2: list[PositionalPosting]
    ) -> list[int]:
        result = []
        i = 0
        j = 0
        while i < len(list1) and j < len(list2):
            if list1[i].doc_id == list2[j].doc_id:
                result.append(list1[i].doc_id)
                i += 1
                j += 1
            elif list1[i].doc_id < list2[j].doc_id:
                i += 1
            else:
                j += 1
        return result

    # Basic Union merge two lists of IndexTerm objects and return the result as list
    def union(self, list1, list2):
        result = []
        i = 0
        j = 0
        while i < len(list1) or j < len(list2):
            if list1[i].docId == list2[j].docId:
                result.append(list1[i].docId)
                i += 1
                j += 1
            elif list1[i].docId < list2[j].docId:
                result.append(list1[i].docId)
                i += 1
            else:
                result.append(list2[j].docId)
                j += 1
        return result

    # Basic AND_Not merge two lists of IndexTerm objects and return the result as list
    def andNot(self, list1, list2):
        result = []
        i = 0
        j = 0
        while i < len(list1) and j < len(list2):
            if list1[i].docId == list2[j].docId:
                i += 1
                j += 1
            elif list1[i].docId < list2[j].docId:
                result.append(list1[i].docId)
                i += 1
            else:
                j += 1
        while i < len(list1):
            result.append(list1[i].docId)
            i += 1
        return result

    # Basic OR_Not merge two lists of IndexTerm objects and return the result as list
    def orNot(self, list1, list2):
        return self.basicUnion(list1, self.basicNot(list2))

    def Not(self, list1, listOfAllDocs):
        result = []
        i = 0
        j = 0
        while i < len(list1) and j < len(listOfAllDocs):
            if list1[i].docId == listOfAllDocs[j].docId:
                i += 1
                j += 1
            elif list1[i].docId < listOfAllDocs[j].docId:
                i += 1
            else:
                result.append(listOfAllDocs[j].docId)
                j += 1
        while j < len(listOfAllDocs):
            result.append(listOfAllDocs[j].docId)
            j += 1
        return result

    # Advanced Intersect merge two lists of IndexTerm objects and return the result as list
    # This is the advanced intersect algorithm
    def advancedIntersect(self, terms):
        terms = self.sortByTermFrequency(terms)
        result = terms[0]
        terms = terms[1:]
        i = 0
        j = 0
        while i < len(terms) and j < len(result):
            # TODO check why list = terms[0]
            list = terms[0]
            result = self.advancedIntersect(result, terms[0])
            terms = terms[1:]
        return result

    def advancedUnion(self, terms):
        terms = self.sortByTermFrequency(terms)
        result = terms[0]
        terms = terms[1:]
        i = 0
        j = 0
        while i < len(terms) or j < len(result):
            # TODO check why list = terms[0]
            list = terms[0]
            result = self.advancedUnion(result, terms[0])
            terms = terms[1:]
        return result

    def advancedAndNot(self, terms):
        terms = self.sortByTermFrequency(terms)
        result = terms[0]
        terms = terms[1:]
        i = 0
        j = 0
        while i < len(terms) and j < len(result):
            # TODO check why list = terms[0]
            list = terms[0]
            result = self.advancedAndNot(result, terms[0])
            terms = terms[1:]
        return result

    def advancedOrNot(self, terms):
        terms = self.sortByTermFrequency(terms)
        result = terms[0]
        terms = terms[1:]
        i = 0
        j = 0
        while i < len(terms) and j < len(result):
            # TODO check why list = terms[0]
            list = terms[0]
            result = self.advancedOrNot(result, terms[0])
            terms = terms[1:]
        return result

    # Sort the list of IndexTerm objects by term frequency
    def sortByTermFrequency(self, terms):
        return sorted(terms, key=lambda k: k.tf, reverse=True)

    @staticmethod
    def get_k_proximity(
        k: int, pos_a: PositionalPosting, pos_b: PositionalPosting
    ) -> PositionalPosting:
        assert pos_a.doc_id == pos_b.doc_id

        positions = []

        for a in pos_a.positions:
            for b in pos_b.positions:
                if abs(b - a) <= k:
                    positions.append(a + k)

        return PositionalPosting(pos_a.doc_id, positions)

    @staticmethod
    def positional_intersect(
        p1: list[PositionalPosting], p2: list[PositionalPosting], k: int
    ) -> list[PositionalPosting]:
        """
        Returns the positional intersect of p1 and p2 where the terms are at
        most k terms apart.

        This function can be used to implement the proximity operator and phrase
        queries.
        """
        answer: list[PositionalPosting] = []
        i = 0
        j = 0

        while i < len(p1) and j < len(p2):
            if p1[i].doc_id == p2[j].doc_id:
                l = []
                pp1 = p1[i].positions
                pp2 = p2[j].positions
                pp1_i = 0

                while pp1_i < len(pp1):
                    pp2_i = 0
                    while pp2_i < len(pp2):
                        if abs(pp1[pp1_i] - pp2[pp2_i]) <= k:
                            l.append(pp2[pp2_i])
                        elif pp2[pp2_i] > pp1[pp1_i]:
                            break
                        pp2_i += 1
                    while l != [] and abs(l[0] - pp1[pp1_i]) > k:
                        del l[0]

                    answer += [
                        PositionalPosting(p1[i].doc_id, [pp1[pp1_i], pos]) for pos in l
                    ]
                    pp1_i += 1

                i += 1
                j += 1
            elif p1[i].doc_id < p2[j].doc_id:
                i += 1
            else:
                j += 1

        return answer

    # Sort the list of IndexTerm objects by term frequency
    def sortByTermFrequency(self, terms):
        return sorted(terms, key=lambda k: k.tf, reverse=True)

    @staticmethod
    def get_k_proximity(
        k: int, pos_a: PositionalPosting, pos_b: PositionalPosting
    ) -> PositionalPosting:
        assert pos_a.doc_id == pos_b.doc_id

        positions = []

        for a in pos_a.positions:
            for b in pos_b.positions:
                if abs(b - a) <= k:
                    positions.append(a + k)

        return PositionalPosting(pos_a.doc_id, positions)
