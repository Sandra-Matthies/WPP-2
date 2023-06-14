#!/usr/bin/env python

import os

target_dir = f"{os.getcwd()}/CISI.ALL.docs"
os.makedirs(target_dir, exist_ok=True)

with open("./CISI.ALL", "r") as f:
    doc_id = -1
    abstract = ""

    while True:
        line = f.readline()
        if not line:
            break

        print(line)

        line = line.strip()

        if not line.startswith(".I "):
            continue

        doc_id = line[3:].strip()

        while not line.startswith(".W"):
            line = f.readline()

        line = f.readline().strip()

        while not line.startswith(".X"):
            abstract += line
            line = f.readline()

        with open(f"{target_dir}/{doc_id}", "w") as out:
            out.write(abstract)

        doc_id = -1
        abstract = ""
