# Generation specification

Version: 1.2.0

The canonical executable prompt is [prompt_template.md](prompt_template.md). It defines the
German–Chinese A1/A2 reference schema used by the included public demo. The orchestration layer
must pass the rendered prompt to a generation agent and the resulting draft to a distinct review
agent invocation.

Input TSV always begins with `word` and may include an optional `expected_pos` column. Exact
surface-form duplicates remain invalid unless every occurrence has a non-empty, unique
`expected_pos` value. This supports legitimate homographs such as the same spelling used as an
adjective and as a verb without changing the output `word` identity. Rendered POS hints are
metadata and must not be copied into the `word` field.

External POS hints are normalized to the canonical output enum. The schema intentionally preserves
German lexical distinctions required by production data, including `contraction` → `Kontraktion`,
`num` → `Numerale`, and `postp` → `Postposition`, rather than collapsing them into `Phrase` or
`Präposition`.

The pipeline enforces two kinds of quality control:

1. Agent judgment: generation and independent review evaluate language content record by record.
2. Mechanical validation: JSON parsing, row count, field count and order, indices, exact input
   preservation, expected-POS alignment when supplied, enum allow-lists, and a few cross-field
   invariants.

Mechanical validation deliberately makes no claim that a meaning, form, example, or translation is
linguistically correct. Evaluation and human sampling remain necessary for release decisions.

The literal em dash `—` is the sole missing-value marker. The `source` field records method
provenance, not a dictionary citation.
