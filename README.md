---
gruppe: WPP2-1
mitglieder:
  - Sandra Matthies
  - Lukas Tetz
  - Niklas Vogel
---

# WPP-2 - INR-Teil 1 & 2

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
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  IR System to query the CISI dataset.

Options:
  --help  Show this message and exit.

Commands:
  boolean-retrieval  Use a boolean retrieval model to query the CISI...
  tf-idf             Use a vector space model based on tf-idf to query...

```

### Boolsche IR-System

Das boolsche IR-System unterstützt die folgenden Abfragen:

- Term
- Phrase
- Proximity

Einzelne Abfragen können mit folgenden Operatoren verknüpft werden:

- AND
- OR
- NOT

Klammern `()` können genutzt werden um die Reihenfolge der Abarbeitung von Teil Abfragen ändern zu
können.

Es können auch Bag of Words abfragen ausgeführt werden, wobei die Queries hierbei aus der Datei
[CSI.QRY] stammen

### Vektorraum basierte IR-System

Das auf TF-IDF basierende Vektorraum IR-System unterstützt folgende Abfragen:

- Bag of Words Abfragen

## Aufbau

- In [CISI](./CISI/) ist das Skript [extract.py](./CISI/extract.py) mit dem die Dokumente im
  Verzeichnis [CISI.ALL.docs](./CISI/CISI.ALL.docs/) erstellt wurden.
- Ein einfacher Tokenizer ist in `tokenizer.py` implementiert.
- Der Parser ist in `parser.py` zu finden.
- Der normale Index sowie der K-Gramm-Index befinden sich in `index.py`.
- Die verschiedenen Algorithmen für intersect/union etc. sind in `posting.py` implementiert.
- In `main.py` ist das CLI sowie der Code der alles zusammenbindet zu finden.
- In `retrieval.py` wird das Inr-System erzeugt und die Funktionen zum retrieval werden hier
  definiert.
- In `retrieval_metrics` werden Recall, Precision, F1-Score etc. sowie die Tabellen bzw. Diagramme
  berechnet und erzeugt.

## Laufzeiten

Die Laufzeiten für die einzelnen Fragen der PDF `INR Teil 1 - Boolesches IR-System` sind in
[RUNTIMES.md](./RUNTIMES.md) zu finden.
