# Agent independence

Full mode invokes review separately from generation. The reviewer reads the input contract and
draft, re-evaluates every entry, and writes a complete corrected 29-field artifact. Mechanical
validation does not replace this judgment.

Simple mode intentionally omits the second invocation and therefore makes no independent-review
claim. Reports must identify which artifact was merged. Neither mode lets an agent author
`meaning_merged` or examples.
