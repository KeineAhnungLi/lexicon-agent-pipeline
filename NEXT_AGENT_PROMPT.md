# Continuation instructions

Read `README.md`, `AGENTS.md`, and the v2 prompt/schema files before operating the pipeline.

Before a long production generation run, enter Goal mode (or create the environment's equivalent
persistent goal) and keep it active until the requested batches and report are complete. Use
isolated Codex subagents/provider invocations for the bounded batches; do not mechanically fill
linguistic fields or generate the whole lexicon directly in the supervising agent.

Use `project.example.json` as the quality-first baseline: GPT-5.6 Sol, `xhigh`, 200 entries per
batch. Keep private input at ignored `local_inputs/words.tsv`; preserve spelling, order, and an
optional `expected_pos` column without lowercasing, translating, lemmatizing, or deduplicating.

Choose the run mode explicitly:

- `simple`: merge a valid generated 29-field artifact.
- `full`: independently review the draft and merge the valid reviewed 29-field artifact.

The final file has 30 fields only because the merger inserts mechanically derived
`meaning_merged`. Agents must not write it or any example field. Do not bypass validation or mark a
failed artifact reviewed. Manifest v1 is incompatible with contract 2.0.0; recreate the workspace
with `prepare`.

For long runs, preserve durable manifest state and provenance. Record exact token usage only when
the provider supplies it; otherwise say it is unavailable. Never publish private inputs, outputs,
rendered production prompts, transcripts, credentials, or uncertain data.
