# Pipeline guide

## Configure

Copy `project.example.json` to ignored `project.json`. Paths are relative to the configuration file,
which makes the project portable. The workspace must be a descendant of that directory. CLI
overrides are available for `--workspace`, `--provider`, and `--batch-size`.

For formal production, put private word lists under ignored `local_inputs/`. The shipped production
example expects `local_inputs/words.tsv`, uses 200 entries per batch, and configures Codex CLI with
`gpt-5.6-sol` plus `reasoning_effort: xhigh`. Change those values deliberately when running another
model or quality/cost profile.

Input is UTF-8 TSV. Its first column must be `word`; an optional `expected_pos` column may be used as
a disambiguation constraint. First-column values are preserved after line-boundary trimming. Empty
entries are rejected. Exact duplicate surface forms are rejected unless every occurrence has a
non-empty, unique `expected_pos`, for example:

```text
word	expected_pos
überlegen	adj
überlegen	verb
```

The rendered `[expected_pos=...]` annotation is metadata, not part of `word`; validation requires
the final canonical `pos` to match recognized hints. If an outer agent converts another tabular
format into this TSV contract, it must preserve lexical entry text and order and must not lowercase,
lemmatize, translate, or deduplicate. It may preserve a source POS column as `expected_pos` so that
legitimate homographs remain distinct rows.

## Audit, prepare, render

`audit` checks that configured files exist. `prepare` reads UTF-8 (including BOM) input, validates
homograph identity rules, snapshots it, and creates batches. It refuses to replace non-empty state
unless the caller passes `--force-reset --yes`. `render` substitutes batch identifiers, indices,
words, and optional POS hints into the versioned prompt.

Inspect the first rendered prompt before a paid run:

```bash
lexicon-pipeline inspect-prompt --batch 1 --show
```

## Run and recover

`run` validates after each provider call. Full mode generates then independently reviews. With
`CodexCLIProvider`, generation and review are separate `codex exec` processes. The configured
`model` and `reasoning_effort` therefore apply independently to both stages.

Generation-only ends with an explicit `generated` state; review-only refuses batches without a
valid draft. On restart:

- valid reviewed artifact → skip;
- valid generated artifact without valid review → resume review;
- missing or invalid draft → generate;
- failed provider or validation → record error and stop.

Fix the cause and rerun; do not mark a failed file reviewed manually.

Use `run --start-batch 7` to ignore earlier manifest batches, or `run --batch 7` for one batch.
`--generation-only` and `--review-only` are shortcuts for the corresponding explicit mode.

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

A standard quality-first run is:

```bash
lexicon-pipeline audit
lexicon-pipeline prepare
lexicon-pipeline render
lexicon-pipeline inspect-prompt --batch 1 --show
lexicon-pipeline run
lexicon-pipeline merge
lexicon-pipeline report
```
