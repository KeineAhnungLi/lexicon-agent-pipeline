# Error taxonomy

| Layer | Example codes/failures | Response |
|---|---|---|
| Configuration | missing key, unsafe workspace, unknown provider | correct config; do not run |
| Input | empty list, duplicate entry, encoding error | repair authorized source |
| Rendering | unresolved placeholder, missing prompt | repair/version prompt |
| Provider | executable absent, timeout, non-zero exit, no artifact | inspect local transcript and retry |
| Syntax | invalid JSON, blank line, non-object | regenerate or review |
| Structure | row count, field order/type, index, word mismatch | repair entire batch |
| Controlled values | level/POS/register/region outside allow-list | correct record or schema version |
| Cross-field | example/translation mismatch, missing meaning | independent review |
| State | no valid draft for review, unreviewed merge attempt | resume required stage |
| Semantic | wrong sense, grammar, translation, example | human/agent evaluation; validator cannot prove |
| Public release | secret/path/private file/large file/license mismatch | remove issue and audit again |

Semantic review uses these finer labels: lexical-category error, morphology error, pronunciation
error, semantic substitution, homograph confusion, missing core sense, hallucinated sense,
collocation error, government/case error, cross-field inconsistency, pedagogical-level error, and
formatting error.

Observed private-project patterns are described only in anonymized form: capitalization homographs
can swap senses; an adverb can be mapped to adjective-only options; a selected-option prefix can
disagree with the class field; a reflexive separable verb can lose `sich`; and a frequent
preposition can omit its core sense or governed case.
