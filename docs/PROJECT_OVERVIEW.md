# Project overview

Lexicon Agent Pipeline turns a line-oriented headword list into reviewed structured JSONL. It
separates semantic work from orchestration so that scripts cannot silently substitute suffix
guessing, lookup tables, or templated translations for agent judgment.

The reference implementation uses two independent provider invocations:

1. Generation reads a rendered batch prompt and authors every record.
2. Review reads both that prompt and the complete draft, corrects every record, and writes a new
   complete artifact.

The orchestrator handles deterministic work only: batching, paths, state, hashes, subprocesses,
mechanical validation, recovery, merge, and reports. Review output is the only merge source.

The included public demo is deliberately small and synthetic. A prior private use case processed
4,812 entries, but neither that list nor its output is distributed here.
