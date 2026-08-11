# Mechanical validation

Agent-stage validation checks JSONL parsing, 29-key order, types, row count, global `first`, exact
`word`, class domains and mappings, the `correct_option` prefix, required `meaning1`, and seven
collocation/translation pairs. It rejects `meaning_merged` and example fields.

Final validation checks the 30-key order and additionally requires `meaning_merged` to equal
`；`.join of the non-`—` numbered meanings. Merge revalidates its selected source and final output.

Mechanical PASS does not establish gender, inflection, pronunciation, meaning, sense coverage,
collocation naturalness, or translation quality. Those require independent review and human
sampling.
