# Architecture

```text
ProjectConfig
  ├─ prepare → manifest + immutable input snapshot
  ├─ render → one generation prompt per batch
  └─ orchestrate
       ├─ AgentProvider.run(generation) → generated JSONL
       ├─ validator gate
       ├─ AgentProvider.run(review) → reviewed JSONL
       ├─ validator gate + provenance
       └─ reviewed-only merge → report
```

`MockProvider` copies labeled synthetic fixtures for tests and demonstrations. `CodexCLIProvider`
invokes the host CLI. `openai-api` and `anthropic-api` are explicit unimplemented extension names;
selecting either produces an error rather than pretending to work.

`manifest.json` is the durable state machine: prepared, rendered, generated, reviewed, or failed.
Artifact validity is rechecked during recovery, so a stale state string cannot make a corrupt file
mergeable. Writes that establish durable artifacts use temporary files followed by an atomic
replacement.

The current record schema is fixed. New language/schema profiles should introduce separately
versioned schemas, prompts, validators, and migrations rather than changing v1 semantics silently.
