# Pipeline guide

## Configure

Copy `project.example.json` to ignored `project.json`. Paths are relative to the configuration file,
which makes the project portable. The workspace must be a descendant of that directory. CLI
overrides are available for `--workspace`, `--provider`, and `--batch-size`.

Input is UTF-8 TSV. Its first row must be the single header `word`; subsequent first-column values
are preserved exactly after line-boundary trimming. Empty and duplicate entries are rejected rather
than silently normalized.

## Audit, prepare, render

`audit` checks that configured files exist. `prepare` reads UTF-8 (including BOM) input, rejects
empty or duplicate entries, snapshots it, and creates batches. It refuses to replace non-empty
state unless the caller passes `--force-reset --yes`. `render` substitutes only batch identifiers,
indices, and words into the versioned prompt.

## Run and recover

`run` validates after each provider call. Full mode generates then independently reviews.
Generation-only ends with an explicit `generated` state; review-only refuses batches without a
valid draft. On restart:

- valid reviewed artifact → skip;
- valid generated artifact without valid review → resume review;
- missing or invalid draft → generate;
- failed provider or validation → record error and stop.

Fix the cause and rerun; do not mark a failed file reviewed manually.

Use `run --start-batch 7` to ignore earlier manifest batches, or `run --batch 7` for one batch.
`--generation-only` and `--review-only` are shortcuts for the corresponding explicit mode. Inspect
the first rendered prompt with `inspect-prompt --batch 1 --show` before a formal provider run.

## Merge and report

`merge` reads only `.reviewed.jsonl` artifacts whose manifest state is `reviewed`, revalidates every
batch, writes atomically, and validates the global sequence. `report` records prompt/provider
provenance, hashes, batch states, row counts, and the boundary between mechanical PASS and
linguistic verification.

## Formal production runs

Use data you are authorized to process, keep it out of Git, inspect every rendered prompt, and use
a host where Codex CLI is already authenticated. For long multi-batch work, use the host’s durable
goal/task mechanism when available. Bounded subagent delegation is acceptable only when batches
are disjoint and every artifact still passes independent review and mechanical gates.
