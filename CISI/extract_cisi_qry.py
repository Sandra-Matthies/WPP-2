#!/usr/bin/env python

import os
import re

target_dir = f"{os.getcwd()}/CISI.QRY.docs"
os.makedirs(target_dir, exist_ok=True)

regex = re.compile(r"^\.(?:A|B|T|I \d+)$")

with open("./CISI.QRY", "r") as f:
    doc_id = -1
    abstract = ""
    skip_search_i = False

    while True:
        if not skip_search_i:
            line = f.readline()
            if not line:
                break

            line = line.strip()

            if not line.startswith(".I "):
                continue

            doc_id = line[3:].strip()
        else:
            skip_search_i = False

        while not line.startswith(".W"):
            line = f.readline()

        line = f.readline().strip()

        while not regex.match(line):
            abstract += line
            line = f.readline()

        with open(f"{target_dir}/{doc_id}", "w") as out:
            out.write(abstract)

        if line.startswith(".I "):
            doc_id = line[3:].strip()
            skip_search_i = True
        else:
            doc_id = -1

        abstract = ""
