# Prompt versioning

Canonical templates live at `prompts/`. An immutable snapshot and SHA-256 manifest live under
`prompts/versions/v1.0.0/`. A behavior change requires a new semantic version directory and
changelog entry; do not rewrite an already released snapshot.

Each workspace manifest hashes configuration, input, generation prompt, review prompt, generation
specification, examples, and schema. Per-stage provenance adds run IDs, timestamps, provider/model
information, output hashes, and the same dependency hashes.

`inspect-prompt --json` reports the canonical version/hash. `inspect-prompt --batch 1 --show`
displays the exact rendered prompt for preflight review.
