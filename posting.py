class Posting:
    def __init__(self):
        self._posting = {}

    # Basic Insersect merge two lists of IndexTerm objects and return the result as list
    # This is the basic intersect algorithm
    # It is not the optimal algorithm
    def basicIntersect(self, list1, list2):
        result = []
        i = 0
        j = 0
        while i < len(list1) and j < len(list2):
            if list1[i].docId == list2[j].docId:
                result.append(list1[i].docId)
                i += 1
                j += 1
            elif list1[i].docId < list2[j].docId:
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
    
    # TODO: Check logic
    # Basic OR_Not merge two lists of IndexTerm objects and return the result as list
    # This is the basic OR_Not algorithm
    # It is not the optimal algorithm
    def basicOrNot(self, list1, list2):
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
                result.append(list2[j].docId)
                j += 1
        while i < len(list1):
            result.append(list1[i].docId)
            i += 1
        while j < len(list2):
            result.append(list2[j].docId)
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
    
