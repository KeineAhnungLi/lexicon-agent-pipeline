# Next-agent handoff prompt

Work in this repository as the primary orchestrator. Read `README.md`, `AGENTS.md`,
`PUBLIC_DATA_POLICY.md`, `PRIVATE_DATA.md`, `docs/PIPELINE_GUIDE.md`, and the current prompt
snapshots before changing or running production data.

The standard quality-first production profile is defined in `project.example.json`: 200 entries per
batch, `gpt-5.6-sol`, `reasoning_effort: xhigh`, and separate generation / independent-review Codex
invocations. Do not silently substitute a cheaper model, lower reasoning effort, different batch
size, or a single self-review call.

If the repository was cloned by an outer agent from a parent directory that contains only one
word-list file, preserve that source file. Copy or convert it into ignored
`local_inputs/words.tsv`, preserving entry text and order exactly. The first column must be `word`.
If the source contains a useful part-of-speech discriminator, preserve it as an optional
`expected_pos` column. Container-format conversion must not lowercase, lemmatize, translate,
deduplicate, or otherwise normalize lexical content. Never commit the production input.

Exact duplicate surface forms without disambiguation remain an input blocker. However, legitimate
homographs are not duplicates when the source identifies distinct parts of speech. Represent them
as separate rows with the same `word` and unique non-empty `expected_pos` values, for example:

```text
word	expected_pos
überlegen	adj
überlegen	verb
```

Do not alter the lexical surface form to encode POS. The pipeline renders POS as metadata, requires
the output `word` to stay unchanged, and mechanically checks the canonical output `pos` against
recognized POS hints.

Copy `project.example.json` to ignored `project.json`, verify that Codex CLI is installed and already
authenticated, then use the repository CLI rather than reimplementing the pipeline:

```bash
lexicon-pipeline audit
lexicon-pipeline prepare
lexicon-pipeline render
lexicon-pipeline inspect-prompt --batch 1 --show
lexicon-pipeline run
lexicon-pipeline merge
lexicon-pipeline report
```

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
