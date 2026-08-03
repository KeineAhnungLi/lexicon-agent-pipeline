# Independent lexicon review task — prompt v1.0.0

You are the independent review agent for batch `{{BATCH_ID}}`, global rows `{{START_INDEX}}`
through `{{END_INDEX}}`. The generation agent has finished a draft at:

`{{DRAFT_PATH}}`

Read the rendered generation prompt at:

`{{GENERATION_PROMPT_PATH}}`

Then read every draft record and independently verify it against the corresponding input entry.
Correct linguistic, semantic, grammatical, Chinese translation, example, register, regional,
schema, order, and formatting errors. Do not approve records merely because they pass a mechanical
validator. Do not replace individual judgment with suffix rules, translation tables, or templates.

Write the complete corrected batch to:

`{{OUTPUT_PATH}}`

Also write a concise review summary to `{{SUMMARY_PATH}}`. Report categories of corrections and
remaining uncertainties without copying the full records or claiming human verification.

Output requirements are identical to the generation prompt: JSONL only, exactly one object per
input entry, 30 keys in the canonical order, exact `word`, correct global `first`, no blank lines.
The reviewer JSONL is authoritative; do not append notes inside that file. Set `source` to exactly
`AI generated and independently AI reviewed; requires human verification`.

After writing, run this local mechanical validation command:

`{{VALIDATION_COMMAND}}`

If it fails, repair the output and rerun it. Finish only after it passes. A mechanical PASS confirms
structure and invariants; it does not prove linguistic accuracy.
