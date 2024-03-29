from index import PositionalPosting


class Posting:
    @staticmethod
    def intersect(p1: list[int], p2: list[int]) -> list[int]:
        """
        Basic intersect that merges the lists `p1` and `p2` and returns their
        intersection of doc IDs.
        """
        p1, p2 = (p1, p2) if len(p1) <= len(p2) else (p2, p1)
        result = []
        i = 0
        j = 0

        while i < len(p1) and j < len(p2):
            if p1[i] == p2[j]:
                result.append(p1[i])
                i += 1
                j += 1
            elif p1[i] < p2[j]:
                i += 1
            else:
                j += 1

        return result

    @staticmethod
    def union(p1: list[int], p2: list[int]) -> list[int]:
        p1, p2 = (p1, p2) if len(p1) <= len(p2) else (p2, p1)
        """
        Basic union that combines two lists of doc_ids and returns
        their union.
        """
        result: list[int] = []
        i = 0
        j = 0

        while i < len(p1) and j < len(p2):
            if p1[i] == p2[j]:
                result.append(p1[i])
                i += 1
                j += 1
            elif p1[i] < p2[j]:
                result.append(p1[i])
                i += 1
            else:
                result.append(p2[j])
                j += 1

        if i < len(p1):
            result += [p for p in p1[i:]]
        elif j < len(p2):
            result += [p for p in p2[j:]]

        return result

    # Basic AND_Not merge two lists of IndexTerm objects and return the result as list
    def andNot(list1: list[PositionalPosting], list2: list[PositionalPosting]):
        list1, list2 = swapListIfSecondIsSmaller(list1, list2)
        result = []
        i = 0
        j = 0
        while i < len(list1) and j < len(list2):
            if list1[i].doc_id == list2[j].doc_id:
                i += 1
                j += 1
            elif list1[i].doc_id < list2[j].doc_id:
                result.append(list1[i].doc_id)
                i += 1
            else:
                j += 1
        while i < len(list1):
            result.append(list1[i].doc_id)
            i += 1
        return result

    # Basic OR_Not merge two lists of IndexTerm objects and return the result as list
    def orNot(list1: list[PositionalPosting], list2):
        return Posting.union(list1, Posting.Not(list2))

    def Not(p1: list[int], docs: list[int]):
        """
        Returns all doc IDs that are in `docs`, but not in `p1`.
        """
        result: list[int] = []
        i = 0
        j = 0

        while i < len(p1) and j < len(docs):
            if p1[i] == docs[j]:
                i += 1
                j += 1
            elif p1[i] < docs[j]:
                i += 1
            else:
                result.append(docs[j])
                j += 1

        while j < len(docs):
            result.append(docs[j])
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


def swapListIfSecondIsSmaller(list1, list2):
    if len(list1) > len(list2):
        return (list2, list1)
    else:
        return (list1, list2)
