from index import PositionalPosting


class Posting:
    def __init__(self):
        self._posting = {}

    @staticmethod
    # Basic Insersect merge two lists of IndexTerm objects and return the result as list
    # This is the basic intersect algorithm
    # It is not the optimal algorithm
    def basicIntersect(
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
    # This is the basic union algorithm
    # It is not the optimal algorithm
    def basicUnion(self, list1, list2):
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
    # This is the basic AND_Not algorithm
    # It is not the optimal algorithm
    def basicAndNot(self, list1, list2):
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
    # This is the basic OR_Not algorithm
    # It is not the optimal algorithm
    def basicOrNot(self, list1, list2):
        return self.basicUnion(list1, self.basicNot(list2))

    def basicNot(self, list1, listOfAllDocs):
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
    def positionalIntersect(list1, list2, k):
        result = []
        i = 0
        j = 0
        while i < len(list1) and j < len(list2):
            if list1[i].doc_id == list2[j].doc_id:
                liste = []
                positions1 = list1[i].positions
                positions2 = list2[j].positions
                k = 0
                while k < len(positions1):
                    l = 0
                    while l < len(positions2):
                        if abs(positions1[k] - positions2[l]) <= k:
                            liste.append(positions2[k])
                        elif positions2[l] > positions1[k]:
                            break
                        l += 1
                    while liste != [] and abs(liste[0] - positions1[k]) > k:
                        del liste[0]
                    for ps in liste:
                        result.append({list1.doc_id, positions1[k],ps})
                        k += 1 
                i += 1
                j += 1
            elif list1[i].doc_id < list2[j].doc_id:
                i += 1
            else:
                j += 1
        return result
