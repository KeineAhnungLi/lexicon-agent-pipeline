# Next-agent handoff prompt

Work in this repository as the primary orchestrator. Read `README.md`, `AGENTS.md`,
`PUBLIC_DATA_POLICY.md`, `PRIVATE_DATA.md`, `docs/PIPELINE_GUIDE.md`, and the current prompt
snapshots before changing or running production data.

For a formal long lexicon run, create a durable goal when the host exposes goal mode and keep it
active through every required batch, merge, and quality report. Use the manifest as the
machine-readable source of truth.

The primary orchestrator must not author production lexical semantics. For every batch:

1. render and inspect the complete generation prompt;
2. launch a generation Codex/agent invocation that reads every entry and makes individual
   linguistic judgments;
3. mechanically validate its complete JSONL draft and return failures to that stage for repair;
4. launch a new, independent review invocation with the prompt and draft;
5. validate the complete reviewed JSONL and record provenance/review summary;
6. merge only reviewed, mechanically valid artifacts.

When the environment supports Codex subagents, delegate only bounded, disjoint batch work with the
full rendered prompt. Do not ask any subagent or script to infer meaning, translation, examples,
grammar, gender, plural, forms, collocations, or notes through suffix guesses, lookup tables, copied
legacy data, or semantic templates. Do not call a “generate remaining batches” shortcut.

Generated-only state is incomplete. Structural PASS is not semantic correctness. Human/Judge
sampling remains necessary. Never add the private 4,812-entry list, spreadsheets, historical
outputs, raw transcripts, credentials, machine-specific paths, or uncertain examples to Git.

Before handoff, run the offline tests, MockProvider demo, strict validation/schema checks, public
release audit, and available lint/type/docs/container checks. Report any environment-bounded checks
honestly. Do not create another remote, publish Pages, or change the MIT/CC0-1.0 license boundary
without explicit owner authorization.
