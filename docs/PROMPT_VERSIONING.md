# Prompt versioning

Live prompts declare semantic version 2.0.0. The complete immutable snapshot is under
`prompts/versions/v2.0.0/` and includes generation template, review template, generation
specification, and a SHA-256 manifest.

Any change to fields, derivation, agent responsibilities, missing-value rules, or linguistic
instructions requires a new semantic version and snapshot. Editorial changes that can alter model
behavior also require a version bump. Provenance records hashes for live prompts, examples, and
both schemas.

Historical v1 files remain only for audit. Manifest v1 is not compatible with contract 2.0.0 and
must not resume v2 runs.
