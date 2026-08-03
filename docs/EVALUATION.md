# Evaluation framework

This repository provides interfaces, not benchmark claims.

Mechanical validation answers whether an artifact follows the transport contract. Linguistic
evaluation must separately assess meanings, grammar, examples, translations, and metadata.

The package includes:

- deterministic sampling for reproducible human review sets;
- exact-match utilities for fields where a gold reference is appropriate;
- a 0–2 rubric definition for meaning, grammar, example, translation, and metadata;
- an evaluation-record JSON Schema.

Private datasets may be split into prompt examples, development, and hidden holdout partitions.
Record the seed and stratification strategy; never evaluate on prompt examples. Suggested strata
include noun, irregular verb, separable verb, reflexive verb, preposition, polysemy, capitalization
homograph, abbreviation, parenthetical variant, multiword expression, collocation sensitivity, and
pronunciation sensitivity.

The Judge schema preserves word, field, reference, candidate, label, severity, error type, reason,
judge model, prompt version, time, input hash, and human-verification status. Supported labels are
`correct`, `acceptable_variant`, `minor_error`, `major_error`, `missing_core_information`,
`hallucinated_information`, and `needs_human_review`. Human review records can be represented as
JSONL using the same schema; CSV import and adjudication UI remain future work.

A production evaluation should predefine sampling strata (such as part of speech, ambiguity, and
special notation), evaluator qualifications, adjudication, missing-data handling, and acceptance
thresholds. Report denominators and uncertainty. Do not turn the synthetic demo into a claimed
accuracy score.
