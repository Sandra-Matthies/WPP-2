# IR System Testen

Hier sind schon einmal alle Laufzeiten zu den Anfragen die in der PDF unter `Testdaten` stehen:

## OS Information

- OS: Linux 6.2.6-76060206-generic
- CPU: AMD Ryzen 7 5800X 8-Core Processor

## Outputs

```
[TIME]: parse_query: 1.33514404296875e-05 seconds.
[TIME]: build_index: 0.8389260768890381 seconds.
[MAIN]: Handle AND query part "information"
[TERM]: Handle term "information"
[MAIN]: Found 586 matches for total query "information"

[TIME]: parse_query: 2.1219253540039062e-05 seconds.
[TIME]: build_index: 0.8533511161804199 seconds.
[MAIN]: Handle AND query part "information"
[TERM]: Handle term "information"
[MAIN]: Handle AND query part "retrieval"
[TERM]: Handle term "retrieval"
[MAIN]: Found 176 matches for total query "information AND retrieval"

[TIME]: parse_query: 2.4080276489257812e-05 seconds.
[TIME]: build_index: 0.8510549068450928 seconds.
[MAIN]: Handle AND query part "information"
[TERM]: Handle term "information"
[MAIN]: Handle AND query part "NOT retrieval"
[TERM]: Handle term "retrieval"
[NOT]: Handle NOT query part "NOT retrieval"
[NOT]: Found 1216 documents for NOT query "NOT retrieval"
[MAIN]: Found 410 matches for total query "information AND NOT retrieval"

[TIME]: parse_query: 4.00543212890625e-05 seconds.
[TIME]: build_index: 0.8308613300323486 seconds.
[MAIN]: Handle AND query part "(information OR data)"
[GROUP]: Handle group query "(information OR data)"
[TERM]: Handle term "information"
[TERM]: Handle term "data"
[GROUP]: Found 744 documents for query "(information OR data)"
[MAIN]: Handle AND query part "analysis"
[TERM]: Handle term "analysis"
[MAIN]: Found 110 matches for total query "(information OR data) AND analysis"

[TIME]: parse_query: 1.3828277587890625e-05 seconds.
[TIME]: build_index: 0.8382589817047119 seconds.
[MAIN]: Handle AND query part ""information retrieval""
[PHRASE]: Handle phrase query ""information retrieval""
[MAIN]: Found 87 matches for total query ""information retrieval""

[TIME]: parse_query: 2.3365020751953125e-05 seconds.
[TIME]: build_index: 0.8373651504516602 seconds.
[MAIN]: Handle AND query part "information /10 retrieval"
[PROX]: Handle proximity query "information /10 retrieval"
[PROX]: Found 215 matches for proximity query "information /10 retrieval"
[MAIN]: Found 215 matches for total query "information /10 retrieval"

[TIME]: parse_query: 3.24249267578125e-05 seconds.
[TIME]: build_index: 0.8486354351043701 seconds.
[MAIN]: Handle AND query part "information /10 retrieval"
[PROX]: Handle proximity query "information /10 retrieval"
[PROX]: Found 215 matches for proximity query "information /10 retrieval"
[MAIN]: Handle AND query part ""library of congress""
[PHRASE]: Handle phrase query ""library of congress""
[MAIN]: Found 0 matches for total query "information /10 retrieval AND "library of congress""

[TIME]: parse_query: 1.239776611328125e-05 seconds.
[TIME]: build_index: 0.8392996788024902 seconds.
[MAIN]: Handle AND query part "daat"
[TERM]: Handle term "daat"
[TERM]: Found less than r=1 documents for term "daat"
[SPELL]: Spell checker uses k-gram index with k=3 for term "daat"
[TIME]: build_k_gram_index: 0.0018191337585449219 seconds.
[SPELL]: Found 0 documents for term "daat"
[MAIN]: Found 0 matches for total query "daat"

[TIME]: parse_query: 1.239776611328125e-05 seconds.
[TIME]: build_index: 0.8355412483215332 seconds.
[MAIN]: Handle AND query part "daat"
[TERM]: Handle term "daat"
[TERM]: Found less than r=1 documents for term "daat"
[SPELL]: Spell checker uses k-gram index with k=2 for term "daat"
[TIME]: build_k_gram_index: 0.002793550491333008 seconds.
[SPELL]: Found 1037 documents for term "daat"
[MAIN]: Found 1037 matches for total query "daat"

[TIME]: parse_query: 1.33514404296875e-05 seconds.
[TIME]: build_index: 0.838165283203125 seconds.
[MAIN]: Handle AND query part "reserch"
[TERM]: Handle term "reserch"
[TERM]: Found less than r=1 documents for term "reserch"
[SPELL]: Spell checker uses k-gram index with k=6 for term "reserch"
[TIME]: build_k_gram_index: 0.0018622875213623047 seconds.
[SPELL]: Found 0 documents for term "reserch"
[MAIN]: Found 0 matches for total query "reserch"

[TIME]: parse_query: 1.2874603271484375e-05 seconds.
[TIME]: build_index: 0.8399481773376465 seconds.
[MAIN]: Handle AND query part "reserch"
[TERM]: Handle term "reserch"
[TERM]: Found less than r=1 documents for term "reserch"
[SPELL]: Spell checker uses k-gram index with k=5 for term "reserch"
[TIME]: build_k_gram_index: 0.0025298595428466797 seconds.
[SPELL]: Found 4 documents for term "reserch"
[MAIN]: Found 4 matches for total query "reserch"

[TIME]: parse_query: 1.2874603271484375e-05 seconds.
[TIME]: build_index: 0.8377413749694824 seconds.
[MAIN]: Handle AND query part "reserch"
[TERM]: Handle term "reserch"
[TERM]: Found less than r=1 documents for term "reserch"
[SPELL]: Spell checker uses k-gram index with k=4 for term "reserch"
[TIME]: build_k_gram_index: 0.0031282901763916016 seconds.
[SPELL]: Found 326 documents for term "reserch"
[MAIN]: Found 326 matches for total query "reserch"

[TIME]: parse_query: 1.2874603271484375e-05 seconds.
[TIME]: build_index: 0.8411974906921387 seconds.
[MAIN]: Handle AND query part "reserch"
[TERM]: Handle term "reserch"
[TERM]: Found less than r=1 documents for term "reserch"
[SPELL]: Spell checker uses k-gram index with k=3 for term "reserch"
[TIME]: build_k_gram_index: 0.003944873809814453 seconds.
[SPELL]: Found 326 documents for term "reserch"
[MAIN]: Found 326 matches for total query "reserch"

[TIME]: parse_query: 1.33514404296875e-05 seconds.
[TIME]: build_index: 0.8340470790863037 seconds.
[MAIN]: Handle AND query part "reserch"
[TERM]: Handle term "reserch"
[TERM]: Found less than r=1 documents for term "reserch"
[SPELL]: Spell checker uses k-gram index with k=2 for term "reserch"
[TIME]: build_k_gram_index: 0.006928205490112305 seconds.
[SPELL]: Found 326 documents for term "reserch"
[MAIN]: Found 326 matches for total query "reserch"

[TIME]: parse_query: 1.3113021850585938e-05 seconds.
[TIME]: build_index: 0.8341770172119141 seconds.
[MAIN]: Handle AND query part "analysi"
[TERM]: Handle term "analysi"
[TERM]: Found less than r=1 documents for term "analysi"
[SPELL]: Spell checker uses k-gram index with k=6 for term "analysi"
[TIME]: build_k_gram_index: 0.0019884109497070312 seconds.
[SPELL]: Found 183 documents for term "analysi"
[MAIN]: Found 183 matches for total query "analysi"

[TIME]: parse_query: 1.2874603271484375e-05 seconds.
[TIME]: build_index: 0.8394296169281006 seconds.
[MAIN]: Handle AND query part "analysi"
[TERM]: Handle term "analysi"
[TERM]: Found less than r=1 documents for term "analysi"
[SPELL]: Spell checker uses k-gram index with k=5 for term "analysi"
[TIME]: build_k_gram_index: 0.0025153160095214844 seconds.
[SPELL]: Found 183 documents for term "analysi"
[MAIN]: Found 183 matches for total query "analysi"

[TIME]: parse_query: 1.2874603271484375e-05 seconds.
[TIME]: build_index: 0.837355375289917 seconds.
[MAIN]: Handle AND query part "analysi"
[TERM]: Handle term "analysi"
[TERM]: Found less than r=1 documents for term "analysi"
[SPELL]: Spell checker uses k-gram index with k=4 for term "analysi"
[TIME]: build_k_gram_index: 0.0031082630157470703 seconds.
[SPELL]: Found 183 documents for term "analysi"
[MAIN]: Found 183 matches for total query "analysi"

[TIME]: parse_query: 1.3113021850585938e-05 seconds.
[TIME]: build_index: 0.8389461040496826 seconds.
[MAIN]: Handle AND query part "analysi"
[TERM]: Handle term "analysi"
[TERM]: Found less than r=1 documents for term "analysi"
[SPELL]: Spell checker uses k-gram index with k=3 for term "analysi"
[TIME]: build_k_gram_index: 0.0038971900939941406 seconds.
[SPELL]: Found 183 documents for term "analysi"
[MAIN]: Found 183 matches for total query "analysi"
```
