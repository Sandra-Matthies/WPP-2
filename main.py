#!/usr/bin/env python

import glob
from os import path

import tokenizer
from index import IndexBuilder, IndexTerm
from posting import Posting


def main():
    builder = IndexBuilder()

    for file in glob.iglob("./CISI/CISI.ALL.docs/*"):
        doc_id = path.basename(file)
        for token in tokenizer.tokenize(file):
            builder.add(IndexTerm(token, doc_id))

    index = builder.build()
    posting = Posting()

def read_query():
    query = input("Enter query: ")
    print("Query is: ", query)
    return query

def getTermType(term):
    if "/" in term:
        return 0
    else:
        return 1

def extractK(query):
    k =[]
    for i in range(0,query.length()):
        if query[i] == "/":
            k.append({i, query[i+1:]}), 
    return k

def get_operators(query):
    operators = []
    if "AND" in query:
        operators.append({query.rfind("AND"),"AND"})
    if "OR" in query:
        operators.append({query.rfind("OR"),"OR"})
    if "AND_NOT" in query:
        operators.append({query.rfind("AND_NOT"),"AND_NOT"})
    if "NOT" in query:
        operators.append({query.rfind("NOT"),"NOT"})
    if "OR_NOT" in query:
        operators.append({query.rfind("OR_NOT"),"OR_NOT"})
    else:
        return operators

def parse_query(query):
    query = query.split()
    return query

def get_posting_list(query, posting):
    posting_list = []
    for term in query:
        posting_list.append(posting.get_posting_list(term))
    return posting_list


if __name__ == "__main__":
    main()
