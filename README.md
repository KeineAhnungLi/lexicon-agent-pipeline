# Lexicon Agent Pipeline

Reproducible orchestration for a German–Chinese learner lexicon with two execution modes and one
shared data contract.

> **Public-data boundary:** this repository contains only 15 newly authored synthetic demo entries.
> It does **not** contain the private 4,812-entry legacy list, other production lists, source spreadsheets, historical outputs, raw
> transcripts, credentials, or third-party dictionary/corpus data.
> No private production data is included.

> **Quality boundary:** validator PASS confirms serialization, identity, field rules, and mechanical
> invariants. It does not prove linguistic accuracy. Human sampling remains required.

## Contract

Generation and independent review produce exactly 29 ordered fields:

`first`, `word`, `spell_word`, `class_options`, `class`, `change`, `pronunciation`,
`correct_option`, followed by seven `meaningN`, `collocationN`, `collocationN_translation` groups.

Agents do not generate examples or `meaning_merged`. Final export has 30 fields because the merger
inserts `meaning_merged` immediately after `correct_option` by joining all non-`—` meanings in
order with the full-width semicolon `；`.

- Agent schema: `schemas/lexicon_agent_record.schema.json`
- Final schema: `schemas/lexicon_record.schema.json`
- Contract and prompt version: `2.0.0`

## Execution modes

- `simple`: generation → validation → merge from the valid `.generated.jsonl` artifact.
- `full`: generation → validation → independent review → validation → merge from the valid
  `.reviewed.jsonl` artifact.

Both modes use the same 29-field agent contract and deterministic final derivation. A full-mode
review artifact is never silently substituted with the draft. Recovery validates artifacts rather
than trusting manifest state alone.

## Offline demo

```bash
python -m pip install -e .
lexicon-pipeline --config examples/project.demo.json demo --reset
```

The MockProvider copies synthetic 29-field fixtures without calling a model. The merger creates a
30-field final file under ignored runtime directories.

## Production profile

Copy `project.example.json` to ignored `project.json`, place the private TSV at
`local_inputs/words.tsv`, then run:

```bash
lexicon-pipeline --config project.json audit
lexicon-pipeline --config project.json prepare
lexicon-pipeline --config project.json render
lexicon-pipeline --config project.json run --mode full
lexicon-pipeline --config project.json merge
lexicon-pipeline --config project.json report
```

The reference quality-first configuration uses GPT-5.6 Sol, `xhigh` reasoning, and 200 entries per
batch. The simple mode uses the same model defaults while skipping the separate review invocation.
Authentication remains host-managed and is never stored here.

To run the simple path, replace the final three commands above with:

```bash
lexicon-pipeline --config project.json run --mode generation-only
lexicon-pipeline --config project.json merge --stage generated
lexicon-pipeline --config project.json report --stage generated
```

If a provider transcript exposes an exact token count, reports may record it. Missing token data is
reported as unavailable; it is never fabricated or presented as exact.

## Input and recovery

Input is UTF-8 TSV beginning with `word`; optional `expected_pos` disambiguates homographs. The
lexical spelling, order, and global numbering are preserved. Manifest v2 records contract version
and separate hashes for agent and final schemas. A v1 manifest belongs to the old contract and must
be recreated with `prepare`; it is not resumed silently.

Valid reviewed batches resume as complete in full mode. Valid generated-only batches resume at
review in full mode and are directly mergeable in simple mode. Invalid or partial artifacts are
never merged.

## Repository map

- `src/lexicon_pipeline/`: CLI, providers, recovery, validation, merge, reporting, evaluation.
- `prompts/`: live v2 prompts and immutable version snapshots.
- `schemas/`: agent, final, manifest, and evaluation JSON Schemas.
- `examples/`: public synthetic demo input and agent records.
- `tests/fixtures/mock/`: public synthetic provider fixtures.
- `docs/`: architecture, contracts, operation, recovery, security, and evaluation.

Code and documentation are MIT licensed. Public synthetic fixtures are CC0-1.0; see
`DATA_LICENSE`. See `PRIVATE_DATA.md` and `PUBLIC_DATA_POLICY.md` before publishing changes.
