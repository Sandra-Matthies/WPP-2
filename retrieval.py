import math
from abc import ABC, abstractmethod

import tokenizer
from index import Index


class RankedResult:
    """Describes the result of a ranked retrieval query."""

    def __init__(self, doc_id: int, score: float):
        """
        Create a new RankedResult.

        doc_id: The document id of the result.
        score: The higher score, the more relevant this document is.
        """
        self.doc_id = doc_id
        self.score = score

    def __repr__(self) -> str:
        return f"RankedResult(doc_id={self.doc_id}, score={self.score})"


class InitRetrievalSystem(ABC):
    @abstractmethod
    def __init__(self, doc_ids: list[int]):
        self.doc_ids = doc_ids
        pass

    @abstractmethod
    def retrieve(self, query: str) -> list[RankedResult]:
        pass

    @abstractmethod
    def retrieve_k(self, query: str, k: int) -> list[RankedResult]:
        pass


class TFIDFRetrievalSystem(InitRetrievalSystem):
    def __init__(self, index: Index):
        super().__init__(index.doc_ids)
        self._index = index

    def retrieve(self, query: str) -> list[RankedResult]:
        tokens = list(map(lambda x: x[0], tokenizer.tokenize_text(query)))
        return self._fast_cosine_score(tokens)

    def retrieve_k(self, query: str, k: int) -> list[RankedResult]:
        tokens = list(map(lambda x: x[0], tokenizer.tokenize_text(query)))
        return self._fast_cosine_score(tokens)[:k]

    def _fast_cosine_score(self, query: list[str]) -> list[RankedResult]:
        """
        Implements the fast cosine score algorithm from chapter 8 slide 9.

        Takes in a tokenized query and returns a list of ranked results.
        """
        # Mapping from doc id to score.
        scores: dict[int, float] = {}

        num_docs = len(self._index.doc_ids)
        avg_doc_len = self._index.avg_doc_length

        for term in query:
            posting_list = self._index.get_posting_list(term)

            if posting_list is None:
                continue

            df_t = posting_list.doc_freq

            for doc_id in posting_list.doc_ids:
                tf_tq = math.log10(query.count(term) + 1)
                tf_td = posting_list.get_term_frequency(doc_id)
                doc_len = self._index.doc_lengths[doc_id]

                wf_td = self._weighted_term_value(
                    tf_tq, tf_td, df_t, num_docs, doc_len, avg_doc_len
                )

                scores[doc_id] = scores.get(doc_id, 0) + wf_td

        for doc_id in scores.keys():
            scores[doc_id] /= float(self._index.doc_lengths[doc_id])

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        ranked_results = list(map(lambda x: RankedResult(x[0], x[1]), sorted_scores))

        return ranked_results

    def _weighted_term_value(
        self,
        tf_tq: int,
        tf_td: int,
        df_t: int,
        num_docs: int,
        doc_len: int,
        avg_doc_len: int,
    ) -> float:
        """Implementation of the weighting function from chapter 7 slide 41."""
        k = 2  # Should be in the range [1.2, 2] (slide 42)
        return (
            tf_tq
            * (tf_td / (tf_td + k * (doc_len / avg_doc_len)))
            * math.log(num_docs / df_t)
        )
