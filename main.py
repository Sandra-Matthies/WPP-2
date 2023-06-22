#!/usr/bin/env python

import glob
import sys
import time
from os import path

import click

import tokenizer
from index import Index, IndexBuilder, IndexTerm, KGramIndex, PositionalPosting
from input_parser import (
    GroupQuery,
    PhraseQuery,
    ProxQuery,
    Query,
    QueryType,
    TermQuery,
    parse,
)
from posting import Posting
from retrieval import TFIDFRetrievalSystem
from retrieval_metrics import Evaluation


def eprint(category: str, text: str):
    """
    Prints `text` to stderr. If `category` is not empty, it will be used as a
    prefix.
    """
    if category == "":
        print(text, file=sys.stderr)
    else:
        print(f"[{category}]: {text}", file=sys.stderr)


def measure_time(func):
    """
    Executes `func` and prints its execution time on stderr.
    """

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        eprint("TIME", f"{func.__name__}: {end - start} seconds.")
        return result

    return wrapper


@measure_time
def build_index() -> Index:
    builder = IndexBuilder()

    for file in glob.iglob("./CISI/CISI.ALL.docs/*"):
        doc_id = int(path.basename(file))
        pos = 0
        for token, pos in tokenizer.tokenize(file):
            pos += 1
            builder.add(IndexTerm(token, doc_id, pos))
        builder.set_doc_len(doc_id, pos)

    return builder.build()


@measure_time
def parse_query(query) -> list[Query]:
    return parse(query)


def getOrQueryTerms(query) -> list[Query]:
    queryList = []
    for term in query.split(" "):
        queryList.append(Query(term, QueryType.OR))
    return queryList


def get_doc_ids(postings: list[PositionalPosting]) -> list[int]:
    """
    Converts a list of positional postings to a list of their respective doc
    IDs.
    """
    return [x.doc_id for x in postings]


def intersect_many(list_of_doc_ids: list[list[int]]) -> list[int]:
    result_doc_ids = list_of_doc_ids[0]

    for right in list_of_doc_ids[1:]:
        result_doc_ids = Posting.intersect(result_doc_ids, right)

    return result_doc_ids


@click.group()
def main():
    """
    IR System to query the CISI dataset.
    """
    pass


@main.command()
def tf_idf():
    """
    Use a vector space model based on tf-idf to query the CISI dataset.
    """
    ir_system = TFIDFRetrievalSystem(build_index())
    Evaluation.execute_evaluation(ir_system=ir_system)


@main.command()
@click.option("-q", "--query", help="Boolean query to search for.", required=True)
@click.option(
    "-k",
    help="k-gram size for the k-gram index.",
    type=click.IntRange(1),
    required=True,
)
@click.option(
    "-r",
    help="Activate spelling correction when less than r documents are found.",
    type=click.IntRange(1),
    default=3,
)
def boolean_retrieval(query, k, r):
    """
    Use a boolean retrieval model to query the CISI dataset.
    """
    # for windows command line
    totalQuery = query
    and_queries = parse_query(query)
    and_query_result_doc_ids: list[list[int]] = []

    index = build_index()

    for query in and_queries:
        eprint("MAIN", f'Handle AND query part "{query}"')
        result_doc_ids: list[int] = []
        if query.type == QueryType.GROUP:
            result_doc_ids = handle_group(index, query, k, r)
        elif query.type == QueryType.OR:
            # We expect OR queries to only consist of two, non-nested parts.
            def handle_part(query: Query) -> list[int]:
                if query.type == QueryType.TERM:
                    return handle_term(index, query, k, r)
                elif query.type == QueryType.PHRASE:
                    return handle_phrase(index, query)
                elif query.type == QueryType.PROX:
                    return handle_prox(index, query)

            left = handle_part(query.parts[0])
            right = handle_part(query.parts[1])
            union = Posting.union(left, right)
            result_doc_ids = union
        elif query.type == QueryType.PROX:
            result_doc_ids = handle_prox(index, query)
        elif query.type == QueryType.PHRASE:
            result_doc_ids = handle_phrase(index, query)
        elif query.type == QueryType.TERM:
            result_doc_ids = handle_term(index, query, k, r)

        if query.is_not:
            eprint("NOT", f'Handle NOT query part "{query}"')
            inverted = Posting.Not(result_doc_ids, index.doc_ids)
            eprint("NOT", f'Found {len(inverted)} documents for NOT query "{query}"')
            and_query_result_doc_ids.append(inverted)
        else:
            and_query_result_doc_ids.append(result_doc_ids)

    if len(and_query_result_doc_ids) == 0:
        eprint("MAIN", f'Found 0 matches for total query "{query}"')
        return

    result_doc_ids = intersect_many(and_query_result_doc_ids)

    if len(result_doc_ids) == 0:
        eprint("MAIN", f'Found 0 matches for total query "{totalQuery}"')
        return

    # Print the result to stdout so it could be used in pipes without the log
    # messages.
    if "/" in totalQuery:
        totalQuery = totalQuery.replace("/", "_")
    with open(totalQuery + ".txt", "w") as file:
        file.write("Query: " + totalQuery + "\n")
        for doc_id in result_doc_ids:
            doc_id_str = str(doc_id)
            file.write(doc_id_str + "\n")
        file.close()

    # Print after outputting the result so we don't have to scroll up.
    eprint(
        "MAIN", f'Found {len(result_doc_ids)} matches for total query "{totalQuery}"'
    )


def handle_prox(index: Index, query: ProxQuery) -> list[int]:
    eprint("PROX", f'Handle proximity query "{query}"')

    postings_a = index.get_positional_postings(query.term_a.term)
    postings_b = index.get_positional_postings(query.term_b.term)

    if postings_a is None or postings_b is None:
        eprint(
            f'Found 0 matches for proximity query term "{query.term_a.term if postings_a is None else query.term_b.term}"'
        )
        return []

    intersect_postings = Posting.positional_intersect(postings_a, postings_b, query.k)

    if len(intersect_postings) == 0:
        eprint("PROX", f'Found 0 matches for proximity query "{query}"')
        return []

    eprint(
        "PROX", f'Found {len(intersect_postings)} matches for proximity query "{query}"'
    )

    return get_doc_ids(intersect_postings)


def handle_phrase(index: Index, query: PhraseQuery) -> list[int]:
    eprint("PHRASE", f'Handle phrase query "{query}"')

    positional_postings = [index.get_positional_postings(x) for x in query.parts]

    if None in positional_postings:
        eprint("PHRASE", f'Found 0 matches for phrase query "{query}"')
        return []

    # Special case single term phrase queries.
    if len(positional_postings) == 1:
        eprint(
            "PHRASE",
            f'Found {len(positional_postings[0])} matches for phrase query "{query}"',
        )
        return get_doc_ids(positional_postings[0])

    # Nested function so we can break from the loop by using `return`.
    def iterate_positional_postings() -> list[int]:
        doc_ids: set[int] = set()

        # Iterate in reverse order to stop at the start of the phrase.
        right = positional_postings[-1]
        for left in reversed(positional_postings[:-1]):
            intersect_postings = Posting.positional_intersect(left, right, 1)
            if len(intersect_postings) == 0:
                eprint("PHRASE", f'Found 0 matches for phrase query "{query}"')
                return []

            for posting in intersect_postings:
                doc_ids.add(posting.doc_id)

            right = intersect_postings

        return list(sorted(doc_ids))

    return iterate_positional_postings()


def handle_term(index: Index, query: TermQuery, k: int, r: int) -> list[int]:
    eprint("TERM", f'Handle term "{query.term}"')

    posting_list = index.get_positional_postings(query.term)

    if len(posting_list) >= r:
        return [x.doc_id for x in posting_list]

    eprint("TERM", f'Found less than r={r} documents for term "{query.term}"')

    return use_spell_checker(query.term, index, k)


def handle_group(index: Index, query: GroupQuery, k: int, r: int) -> list[int]:
    eprint("GROUP", f'Handle group query "{query}"')

    def handle_part(query: Query) -> list[int]:
        if query.type == QueryType.TERM:
            return handle_term(index, query, k, r)
        elif query.type == QueryType.PHRASE:
            return handle_phrase(index, query)
        elif query.type == QueryType.PROX:
            return handle_prox(index, query)
        elif query.type == QueryType.GROUP:
            return handle_group(index, query, k, r)
        elif query.type == QueryType.OR:
            left = handle_part(query.parts[0])
            right = handle_part(query.parts[1])
            union = Posting.union(left, right)
            return union

    results = []
    for q in query.and_queries:
        results.append(handle_part(q))

    # Same handling as in `main` because GROUP queries can consist of multiple
    # AND queries.
    results = intersect_many(results)
    eprint("GROUP", f'Found {len(results)} documents for query "{query}"')

    return results


def get_posting_list(query, posting):
    posting_list = []
    for term in query:
        posting_list.append(posting.get_posting_list(term))
    return posting_list


def computeJaccardCoeffcient(itersectionList, unionList):
    return len(itersectionList) / (len(unionList) - len(itersectionList))


def use_spell_checker(term: str, index: Index, k: int) -> list[int]:
    @measure_time
    def build_k_gram_index():
        k_gram_index = KGramIndex(term)
        k_gram_index.build(k)
        k_gram_index.setKGramValues(index)
        return k_gram_index

    eprint("SPELL", f'Spell checker uses k-gram index with k={k} for term "{term}"')

    k_gram_index = build_k_gram_index()

    # verwende die kgramme mit dem niedrigsten lDist Wert
    k_gram_index.getKGramsWithLowestLDistValue()

    # hole die Postinglisten für die kgramme
    results: list[list[PositionalPosting]] = []
    for kgram in k_gram_index._kgrams:
        kgramResultList = []
        for obj in kgram["values"]:
            kgramResultList += index.get_positional_postings(obj["val"])
        results.append(kgramResultList)

    doc_ids = [posting.doc_id for posting_list in results for posting in posting_list]
    doc_ids = list(sorted(set(doc_ids)))

    eprint("SPELL", f'Found {len(doc_ids)} documents for term "{term}"')
    return doc_ids


if __name__ == "__main__":
    main()
