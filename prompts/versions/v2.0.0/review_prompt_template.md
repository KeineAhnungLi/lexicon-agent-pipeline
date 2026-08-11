# Independent lexicon review — prompt v2.0.0

You are the independent review agent for batch `{{BATCH_ID}}`, global rows `{{START_INDEX}}`
through `{{END_INDEX}}`.

Read the rendered generation prompt at `{{GENERATION_PROMPT_PATH}}`, then inspect every draft record
at `{{DRAFT_PATH}}`. Re-evaluate each entry with your own linguistic judgment. Correct spelling
variants, class, inflection, Chinese meanings, collocations, ordering, and serialization. Do not
approve content merely because it passes mechanical validation, and do not replace judgment with
suffix rules, translation tables, or templates.

Write the complete corrected batch to `{{OUTPUT_PATH}}`. The reviewed artifact must still contain
exactly the generation contract's 29 ordered keys. Do not add `meaning_merged`, examples,
sentences, provenance, notes, or review comments to JSONL. The pipeline will derive
`meaning_merged` only after this reviewed artifact passes validation.

Write a concise operational summary to `{{SUMMARY_PATH}}`, describing categories of corrections
and remaining uncertainty without copying the full records or claiming human verification.

After writing, run:

`{{VALIDATION_COMMAND}}`

Repair and rerun until it passes. A mechanical PASS confirms structure and invariants, not semantic
or grammatical accuracy.
