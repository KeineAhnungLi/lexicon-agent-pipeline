# Agent operating contract

This repository separates orchestration from semantic authorship.

## Required execution model

- The orchestrator prepares batches, renders prompts, launches providers, validates artifacts,
  records provenance, resumes state, merges reviewed outputs, and reports results.
- A generation agent reads each rendered batch prompt and authors every record using linguistic
  judgment.
- A separate review-agent invocation reads the prompt and generated draft, checks every record
  independently, and writes the complete reviewed batch.
- The orchestrator must never fill meanings, translations, examples, grammatical forms, or notes
  through suffix guesses, lookup tables, templates, or a “remaining batches” generator.
- A batch is mergeable only after the reviewed artifact passes mechanical validation.

When the host supports persistent goals, create a goal for a long production run and keep it active
until every required batch, merge, and report is complete. Goal state is a coordination aid, not a
substitute for the manifest.

For large formal runs, the primary agent may delegate bounded generation or audit work to Codex
subagents when the execution environment supports them. Each delegate must receive the full
rendered prompt, operate on disjoint batch files, and return artifacts for the same independent
review and validator gates. Never delegate by asking an agent to invent a rule-based shortcut.

## Public repository boundary

Do not add private word lists, source spreadsheets, historical full outputs, raw transcripts,
credentials, machine-specific absolute paths, or material with uncertain redistribution rights.
Use only the original synthetic demo fixtures included here. Read `PUBLIC_DATA_POLICY.md` and
`PRIVATE_DATA.md` before preparing a release.
