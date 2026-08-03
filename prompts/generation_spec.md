# Generation specification

Version: 1.0.0

The canonical executable prompt is [prompt_template.md](prompt_template.md). It defines the
German–Chinese A1/A2 reference schema used by the included public demo. The orchestration layer
must pass the rendered prompt to a generation agent and the resulting draft to a distinct review
agent invocation.

The pipeline enforces two kinds of quality control:

1. Agent judgment: generation and independent review evaluate language content record by record.
2. Mechanical validation: JSON parsing, row count, field count and order, indices, exact input
   preservation, enum allow-lists, and a few cross-field invariants.

Mechanical validation deliberately makes no claim that a meaning, form, example, or translation is
linguistically correct. Evaluation and human sampling remain necessary for release decisions.

The literal em dash `—` is the sole missing-value marker. The `source` field records method
provenance, not a dictionary citation.
