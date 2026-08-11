# Agent operating contract

The orchestrator and language agents have separate responsibilities.

- A generation agent judges every entry and writes the complete 29-field agent record.
- In `full` mode, a distinct review invocation independently corrects every draft and writes a
  complete 29-field reviewed record.
- In `simple` mode, a mechanically valid generated artifact is the merge source.
- The orchestrator prepares batches, renders prompts, invokes providers, validates artifacts,
  records provenance, recovers state, merges, derives `meaning_merged`, and reports results.
- The sole permitted semantic-looking derivation is exact: insert `meaning_merged` after
  `correct_option` as `；`.join of non-`—` `meaning1` through `meaning7`. It must not summarize,
  translate, deduplicate, or otherwise alter meanings.
- No agent artifact contains `meaning_merged` or example/sentence fields.
- Neither agents nor scripts may fill linguistic content using suffix guesses, translation tables,
  neighboring records, or templates.

For the quality-first profile use GPT-5.6 Sol with `xhigh` reasoning and 200 entries per batch.
Never invent token usage when a provider does not expose an exact count.

For a long production run, the supervising Codex session must create and keep an explicit goal,
then delegate bounded batches to isolated Codex subagents/provider invocations. Do not have the
supervisor synthesize thousands of rows in one turn. In full mode, generation and review for a
batch must be separate invocations; the reviewer reads the draft but must independently correct
it. Validate and persist each batch before dispatching the next one so the run remains resumable.

Do not add private word lists, spreadsheets, production outputs, raw transcripts, credentials,
machine-specific paths, licensed corpora, or uncertain third-party examples. Public fixtures must
be newly authored synthetic data covered by `DATA_LICENSE`.
