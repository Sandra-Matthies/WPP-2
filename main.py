#!/usr/bin/env python

import glob
import sys
import time
from os import path

import click

import tokenizer
from index import Index, IndexBuilder, IndexTerm, KGramIndex, PositionalPosting
from input_parser import Query, QueryType, parse
from posting import Posting


def measure_time(func):
    """
    Executes `func` and prints its execution time on stderr.
    """

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"TIME [{func.__name__}]: {end - start} seconds.", file=sys.stderr)
        return result

    return wrapper


@measure_time
def build_index() -> Index:
    builder = IndexBuilder()

    for file in glob.iglob("./CISI/CISI.ALL.docs/*"):
        doc_id = path.basename(file)
        for token, pos in tokenizer.tokenize(file):
            builder.add(IndexTerm(token, int(doc_id), pos))

    return builder.build()


@measure_time
def parse_query(query) -> list[Query]:
    return parse(query)

def getOrQueryTerms(query) -> list[Query]:
    queryList = []
    for term in query.split(" "):
        queryList.append(Query(term, QueryType.OR))
    return queryList

@click.command()
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
def main(query, k, r):
    and_queries = parse_query(query)

    index = build_index()

    for query in and_queries:
        # TODO: Remove when done
        print(f"DEBUG: {query}")
        # TODO: GROUP and OR queries must be traversed recursively
        #       because GROUP queries can be nested and OR queries
        #       can contain GROUP queries.
        if query.type == QueryType.GROUP:
            print("TODO: GROUP")
        elif query.type == QueryType.OR:
            print("TODO: OR")
            print(query.parts)
            postings_a = None
            postings_b = None
            postings_a=index.get_positional_postings(query.parts[0].term)
            postings_b=index.get_positional_postings(query.parts[1].term)
            resultList = None
            # Only works if the structure is term OR term (max 2 terms)
            if postings_a is not None and postings_b is not None:
                resultList = Posting.union(postings_a, postings_b)
            elif postings_a is not None:
                resultList = postings_a
            elif postings_b is not None:
                resultList = postings_b
            else:
                print("Found 0 matches for OR query")
                break
            print(f"Found {len(resultList)} matches for OR query: {query}")

        elif query.type == QueryType.PROX:
            positional_postings = []

            postings_a = index.get_positional_postings(query.term_a.term)
            postings_b = index.get_positional_postings(query.term_b.term)

            if postings_a is None or postings_b is None:
                print(
                    f"Found 0 matches for proximity query term: {query.term_a.term if postings_a is None else query.term_b.term}"
                )
                break

            intersect_postings = Posting.positional_intersect(
                postings_a, postings_b, query.k
            )

            if len(intersect_postings) == 0:
                print(f"Found 0 matches for proximity query: {query}")
                break

            print(
                f"Found {len(intersect_postings)} matches for proximity query: {query}"
            )
            for posting in intersect_postings:
                print(f"  {posting.doc_id}: {posting.positions}")

        elif query.type == QueryType.PHRASE:
            positional_postings = [
                index.get_positional_postings(x) for x in query.parts
            ]

            if None in positional_postings:
                print(f"Found 0 matches for phrase query: {query}")
                break

            # Special case single term phrase queries.
            if len(positional_postings) == 1:
                print(
                    f"Found {len(positional_postings[0])} matches for phrase query: {query}"
                )
                for posting in positional_postings[0]:
                    print(f"  {posting.doc_id}: {posting.positions}")
                break

            # Nested function so we can break from the loop by using `return`.
            def iterate_positional_postings():
                # Keep track of the start positions of the phrase.
                starts: list[PositionalPosting] = []

                # Iterate in reverse order to stop at the start of the phrase.
                right = positional_postings[-1]
                for left in reversed(positional_postings[:-1]):
                    intersect_postings = Posting.positional_intersect(left, right, 1)
                    if len(intersect_postings) == 0:
                        print(f"Found 0 matches for phrase query: {query}")
                        return

                    starts = [(x.doc_id, x.positions[0]) for x in intersect_postings]
                    right = intersect_postings
                    print(right)

                print(f"Found {len(starts)} matches for phrase query: {query}:")
                for doc_id, start in starts:
                    print(f"  {doc_id}: {start}")

            iterate_positional_postings()

        elif query.type == QueryType.TERM:
            print("TODO: TERM")
            if query.is_not:
                print("TODO: NOT")
            else:
                posting_list = index.get_positional_postings(query.term)
                if posting_list is None:
                    print("0 Results")
                    # Try to find a similar term
                    posting_list = executeKGramm(query.term, index)
                    if posting_list is None or len(posting_list) == 0:
                        print(
                            "Es konnten trotz Rechtschreibkorrektur keine Ergebnisse gefunden werden."
                        )
                    else:
                        for k in posting_list:
                            if k is not None:
                                print("Ergebnis: ", k)
                            else:
                                print(
                                    "Es konnten trotz Rechtschreibkorrektur keine Ergebnisse gefunden werden."
                                )
                else:
                    print("TODO: Output", posting_list)
                if posting_list is not None and len(posting_list) < r:
                    result = executeKGramm(query.term, index)
                    if result is None or len(result) == 0:
                        print(
                            "Es konnten trotz Rechtschreibkorrektur keine Ergebnisse gefunden werden."
                        )
                    else:
                        for k in result:
                            if k is not None:
                                print("Ergebnis: ", k)
                            else:
                                print(
                                    "Es konnten trotz Rechtschreibkorrektur keine Ergebnisse gefunden werden."
                                )


def get_posting_list(query, posting):
    posting_list = []
    for term in query:
        posting_list.append(posting.get_posting_list(term))
    return posting_list


def computeJaccardCoeffcient(itersectionList, unionList):
    return len(itersectionList) / (len(unionList) - len(itersectionList))


# Rechtschreibkorrektur wird nur angewandt, wenn weniger als r Ergebnisse vorliegen
def executeKGramm(term: str, index: Index):
    numberOfLetters = input("Wie Groß soll ein kgramm sein? ")
    start = time.time()
    kGramIndex = KGramIndex(term)
    kGramIndex.build(numberOfLetters)
    kGramIndex.setKGramValues(index)
    end = time.time()
    print(f"k-gram Index built in {end - start} seconds.")
    # verwende die kgramme mit dem niedrigsten lDist Wert
    kGramIndex.getKGramsWithLowestLDistValue()
    # hole die Postinglisten für die kgramme
    resultLists = []
    for kgram in kGramIndex._kgrams:
        kgramResultList = []
        for obj in kgram["values"]:
            kgramResultList.append(index.get_positional_postings(obj["val"]))
        resultLists.append(kgramResultList)
    return resultLists


if __name__ == "__main__":
    main()
