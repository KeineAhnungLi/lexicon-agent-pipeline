# Error taxonomy

| Category | Examples | Response |
|---|---|---|
| Serialization | invalid JSON, blank line, wrong 29/30 order | rewrite complete artifact |
| Identity | row count, `first`, or exact `word` mismatch | restore input alignment |
| Grammar mapping | invalid `class`, `class_options`, or prefix | re-evaluate entry |
| Meaning | missing `meaning1`, wrong sense or label | linguistic correction |
| Collocation | unpaired translation or unnatural usage | correct both fields |
| Derived field | authored, misplaced, or unequal `meaning_merged` | derive again at merge |
| State | wrong merge source for simple/full mode | resume required stage |
| Provenance | unavailable token count presented as exact | mark unavailable |

Mechanical errors block merge. Semantic correctness still requires agent and human evaluation.
