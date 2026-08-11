# Evaluation

The repository provides evaluation interfaces, not benchmark claims. Suggested human or model-judge
dimensions are spelling variants, grammatical class and inflection, Chinese meaning accuracy,
collocation naturalness, and cross-field consistency.

Evaluation samples must not be copied from prompt examples. Stratify private holdouts by noun,
irregular/separable/reflexive verb, adposition, polysemy, capitalization, abbreviation, and
multiword entry. Preserve sampling seeds and distinguish AI review from human verification.

The final `meaning_merged` is evaluated mechanically for exact derivation, not as an independently
authored linguistic field.
