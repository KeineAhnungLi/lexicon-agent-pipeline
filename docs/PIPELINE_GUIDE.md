# Pipeline guide

Copy `project.example.json` to ignored `project.json` and place UTF-8 TSV input at
`local_inputs/words.tsv`. Its first column is `word`; optional `expected_pos` distinguishes
homographs. Preserve lexical text and order exactly.

Prepare and render once, then choose a mode:

```bash
lexicon-pipeline --config project.json prepare
lexicon-pipeline --config project.json render
lexicon-pipeline --config project.json run --mode generation-only
lexicon-pipeline --config project.json merge --stage generated
lexicon-pipeline --config project.json report --stage generated
# or, for the full independently reviewed path:
lexicon-pipeline --config project.json run --mode full
lexicon-pipeline --config project.json merge
lexicon-pipeline --config project.json report
```

Simple mode selects validated `.generated.jsonl`; full mode selects validated `.reviewed.jsonl`.
Both selected artifacts have 29 fields. Merge inserts derived `meaning_merged` and writes the
30-field final file. Never edit state labels to bypass a failed validator.

The production default is GPT-5.6 Sol, `xhigh`, 200 entries per batch. Credentials are host-managed.
Do not publish local input, workspaces, outputs, transcripts, or rendered production prompts.
