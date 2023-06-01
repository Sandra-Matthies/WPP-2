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
        print(f"DEBUG: {query}")
        # TODO: GROUP and OR queries must be traversed recursively
        #       because GROUP queries can be nested and OR queries
        #       can contain GROUP queries.
        if query.type == QueryType.GROUP:
            print("TODO: GROUP")
        elif query.type == QueryType.OR:
            print("TODO: OR")
        elif query.type == QueryType.PROX:
            print("TODO: PROX")
        elif query.type == QueryType.PHRASE:
            print("TODO: PHRASE")
            positional_postings = [
                index.get_positional_postings(x) for x in query.parts
            ]

            if None in positional_postings:
                print("TODO: NO MATCH")
                break

            intersect_doc_ids = Posting.basicIntersect(
                positional_postings[0], positional_postings[1]
            )

            result: list[PositionalPosting] = []

            for doc_id in intersect_doc_ids:
                for posting_list in positional_postings:
                    for positional_posting in posting_list:
                        if positional_posting.doc_id == doc_id:
                            result.append(positional_posting)

            print("INTERSECT", intersect_doc_ids)
            print("RESULT", result)

            new_left = None

            for left, right in zip(result, result[1:]):
                new_left = Posting.get_k_proximity(
                    1, new_left if new_left is not None else left, right
                )
                print(new_left)

            # Posting.get_k_proximity(
            #     1, result[: int(len(result) / 2)], result[int(len(result) / 2) :]
            # )

        elif query.type == QueryType.TERM:
            print("TODO: TERM")
            if query.is_not:
                print("TODO: NOT")
            else:
                posting_list = index.get_positional_postings(query.term)
                if posting_list is None:
                    print("TODO: NOT FOUND")
                else:
                    print("TODO: Output", posting_list)

    # TODO: Remove
    exit(1)

    # Rechtschreibkorrektur wird nur angewandt, wenn weniger als r Ergebnisse vorliegen
    # TODO resultList austauschen mit korrekter Ergebnis Liste
    resultList = [1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 34, 456, 445, 4545, 45]
    term = ""
    numberOfLetters = input("Wie Groß soll ein kgramm sein? ")
    if resultList.length() < r:
        start = time.time()
        kGramIndex = KGramIndex(term)
        kGramIndex.build(numberOfLetters)
        kGramIndex.setKGramValues(index)
        end = time.time()
        print(f"k-gram Index built in {end - start} seconds.")
        # TODO Prüfung welcher Term bei der Suche Verwendet werden soll


def get_posting_list(query, posting):
    posting_list = []
    for term in query:
        posting_list.append(posting.get_posting_list(term))
    return posting_list


def computeJaccardCoeffcient(itersectionList, unionList):
    return len(itersectionList) / (len(unionList) - len(itersectionList))


if __name__ == "__main__":
    main()
