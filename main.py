#!/usr/bin/env python

import glob
from os import path

import tokenizer
from index import IndexBuilder, IndexTerm


def main():
    builder = IndexBuilder()

    for file in glob.iglob("./CISI/CISI.ALL.docs/*"):
        doc_id = path.basename(file)
        for token in tokenizer.tokenize(file):
            builder.add(IndexTerm(token, doc_id))

    index = builder.build()


if __name__ == "__main__":
    main()
