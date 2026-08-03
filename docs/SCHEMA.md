# Record schema

The reference record has exactly 30 ordered keys. JSON objects are unordered by the JSON standard,
but this project deliberately treats serialized key order as a reproducibility contract.

`first` is the one-based global row number and `word` must reproduce the input line exactly.
Inapplicable values use the literal em dash `—`; null and empty strings are rejected. `meaning`
cannot be missing. `example` and `translation` must either both exist or both use the missing
marker.

Allowed enum values are defined in both `schemas/lexicon_record.schema.json` and the mechanical
validator. JSON Schema checks shape and values; pipeline validation additionally checks source
order, global indices, row count, and pair invariants.

The schema describes a German–Chinese A1/A2 profile. It is not presented as a universal multilingual
ontology.
