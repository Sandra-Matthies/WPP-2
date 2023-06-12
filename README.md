# WPP-2

## Installation

Das IR-System ist in Python geschrieben und nutzt ein paar pip-Dependencies die in
`requirements.txt` deklariert sind. Diese können folgendermaßen installiert werden:

```
pip install -r requirements.txt
```

## Ausführung

FÜr einen ersten Überblick kann mit dem Flag `--help` die Hilfe des Programm ausgegeben werden:

```
python ./main.py --help
```

Das führt zu folgender Ausgabe:

```
Usage: main.py [OPTIONS]

Options:
  -q, --query TEXT  Boolean query to search for.  [required]
  -k INTEGER RANGE  k-gram size for the k-gram index.  [x>=1; required]
  -r INTEGER RANGE  Activate spelling correction when less than r documents
                    are found.  [x>=1]
  --help            Show this message and exit.
```

Das IR-System unterstützt die folgenden Abfragen:

- Term
- Phrase
- Proximity

Einzelne Abfragen können mit folgenden Operatoren verknüpft werden:

- AND
- OR
- NOT

Klammern `()` können genutzt werden um die Reihenfolge der Abarbeitung von Teil Abfragen ändern zu
können.

## Laufzeiten

Die Laufzeiten für die einzelnen Fragen der PDF `INR Teil 1 - Boolesches IR-System` sind in
[RUNTIMES.md](./RUNTIMES.md) zu finden.
