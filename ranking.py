import math


class Ranking:
    @staticmethod
    def fastCosineScore(query: list[str], index, k: int):
        # Mapping from doc_id to score.
        queryScores: dict[int, float] = {}
        for term in query:
            if term in index.index:
                wt = Ranking.getQueryWeight()
                for doc in index.index[term]:
                    queryScores[doc.doc_id] = queryScores.get(doc.doc_id, 0) + wt
            for doc in queryScores:
                queryScores[doc] = queryScores[doc] / index.docLengths[doc]
        return queryScores[0:k]

    @staticmethod
    def getQueryWeight(tf: int, df: int, n: int, k: int, doc) -> float:
        """
        Returns the query weight based on the given parameters:

        tf:   term frequency
        df:   document frequency
        n:    number of documents
        k:    constant
        doc:  document
        """
        return tf / (tf + k * (doc.length / doc.avgDocLen)) * math.log(n / df)
