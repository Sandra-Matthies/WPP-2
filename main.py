#!/usr/bin/env python

import glob
from os import path
import time
import tokenizer
from index import IndexBuilder, IndexTerm
from posting import Posting


def main():
    start = time.time()
    builder = IndexBuilder()

    for file in glob.iglob("./CISI/CISI.ALL.docs/*"):
        doc_id = path.basename(file)
        for token in tokenizer.tokenize(file):
            builder.add(IndexTerm(token, doc_id))
    index = builder.build()
    
    end = time.time()
    # Zur Auswertung der Laufzeit des Indexbaus
    print(f"Index built in {end - start} seconds.")
    # TODO Auswertung der Laufzeit der Abfrageverarbeitung
    posting = Posting()
    query = read_query()
    if(getTermType(query)):
        print("Term type is no Proximity ")
    else:
        k = extractK(query)
        if(k.length() > 0):
            print("k is: ", k)
            #query = query[:k[0][0]]

    operators = get_operators(query)
    print("Operators are: ", operators)
    # Rechtschreibkorrektur wird nur angewandt, wenn weniger als r Ergebnisse vorliegen
    # TODO resultList austauschen mit korrekter Ergebnis Liste
    resultList = [1,2,2,3,3,3,3,3,3,3,3,3,34,456,445,4545,45]
    r = input("Wie viele Ergebnisse sollen mindestens vorliegen, damit keine Rechtschreibkorrektur angewandt wird? ")
    if( resultList.length() < r):
        start = time.time()
        index.buildNgramIndex(3)
        end = time.time()
        print(f"k-gram Index built in {end - start} seconds.")


def read_query():
    query = input("Enter query. Please use AND_NOT for AND NOT and OR_NOT for OR NOT: ")
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
