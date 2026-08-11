# Architecture

The orchestrator owns deterministic work: input preparation, batching, prompt rendering, provider
launch, stage-aware validation, provenance, recovery, merging, final derivation, and reporting.
Language agents own spelling, grammar, meanings, and collocations.

```text
simple: input -> generation(29) -> validate -> merge generated -> derive -> final(30)
full:   input -> generation(29) -> validate -> independent review(29) -> validate
        -> merge reviewed -> derive -> final(30)
```

The derivation inserts `meaning_merged` after `correct_option` without modifying any agent-authored
field. Manifest v2 binds a workspace to contract 2.0.0 and separate agent/final schema hashes.
