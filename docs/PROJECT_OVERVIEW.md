# Project overview

Lexicon Agent Pipeline turns an ordered German headword list into structured German–Chinese learner
records. Agents judge entries individually; the host never substitutes suffix rules, lookup tables,
or templated translations for linguistic work.

Both run modes create 29-field agent records without examples or `meaning_merged`. Simple mode
merges validated generation; full mode adds an independent review and merges only reviewed output.
The final 30-field file is deterministic because merge inserts the exact joined meanings.

The public repository demonstrates orchestration with 15 synthetic entries only. Production input,
outputs, transcripts, and source resources stay private.
