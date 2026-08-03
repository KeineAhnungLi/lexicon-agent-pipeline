# lexicon-agent-pipeline

A reproducible dual-agent workflow for structured lexicon generation, independent linguistic
review, mechanical validation, resumable batch execution, and human-calibrated evaluation.

一套面向多语言结构化词库生产的双 Agent Pipeline：生成与审校使用独立上下文，程序仅负责
编排、验证、恢复与合并，不以规则生成语言语义内容。

> **Public-data boundary:** this repository contains only 15 newly authored synthetic demo entries.
> It does **not** contain the non-public 4,812-entry production list, source spreadsheets, historical
> model outputs, or raw agent transcripts.
>
> **Quality boundary:** validator PASS means that JSON, row count, 30-field order, indices, input
> identity, enums, and selected cross-field invariants pass. It does **not** prove linguistic,
> grammatical, or translation accuracy.
>
> **Demo boundary:** CI and `demo` replay labeled MockProvider fixtures and call no paid model.
> Formal Codex runs require a locally installed, already authenticated Codex CLI on the host.
>
> **License:** code, prompts, and documentation use the permissive [MIT License](LICENSE). The
> original synthetic public examples and MockProvider fixtures use [CC0-1.0](DATA_LICENSE).

## What it does

```text
Input Words
    ↓
Batching and Prompt Rendering
    ↓
Generation Agent (independent process)
    ↓
Mechanical Validator
    ↓
Independent Review Agent (new process)
    ↓
Mechanical Validator
    ↓
Judge / Human Sampling
    ↓
Reviewed-only Merge and Quality Report
```

The included reference profile is German–Chinese A1/A2 with a fixed 30-field JSONL schema. The
provider and evaluation interfaces are extensible, but the repository does not claim that the
current prompt is language-independent.

## No-cost reproducible demo

Python 3.10–3.12 is supported.

```bash
python -m venv .venv
# Activate the environment for your shell, then:
python -m pip install -e ".[dev,docs]"
lexicon-pipeline --config examples/project.demo.json demo --reset
```

The command prepares one 15-entry batch, renders the current prompt, replays distinct generation
and review fixtures, validates both, merges only the reviewed output, and writes provenance and
quality reports under ignored `examples/demo_workspace/` and `examples/expected/runtime/`.

Run the release checks:

```bash
ruff check .
mypy
pytest
lexicon-pipeline audit-public-release --root .
mkdocs build --strict
```

## Formal Codex CLI run

Copy `project.example.json` to the ignored local file `project.json`, point `input_file` at data you
are authorized to use, and keep `workspace` inside the repository:

```bash
lexicon-pipeline audit
lexicon-pipeline prepare
lexicon-pipeline render
lexicon-pipeline run
lexicon-pipeline merge
lexicon-pipeline report
```

`CodexCLIProvider` launches generation and review as separate `codex exec` processes. Authentication
is deliberately not embedded in this repository or Docker image. Inspect the locally installed
CLI’s help before adding provider `extra_args`; unsafe sandbox-bypass flags are not defaults.

Useful recovery modes:

```bash
lexicon-pipeline run --mode generation-only
lexicon-pipeline run --mode review-only
lexicon-pipeline run --batch 3
lexicon-pipeline validate --batch 3 --stage reviewed
lexicon-pipeline inspect-prompt --json
```

Generated-only batches resume at review. Valid reviewed batches are skipped. A failed review never
becomes mergeable.

## Motivation and boundaries

Large lexicon jobs need more than one model response: they need immutable input alignment,
independent review, explicit incomplete states, recovery after quota/network/process failures, and
artifacts that can be audited. This project makes those controls reusable while keeping semantic
decisions inside agent or human review.

The current evaluation package is a planned, human-calibrated framework. It defines exact-match,
sampling, rubric, Judge-record, and aggregation interfaces but publishes no accuracy numbers. See
[docs/EVALUATION.md](docs/EVALUATION.md) and [docs/ERROR_TAXONOMY.md](docs/ERROR_TAXONOMY.md).

Current limitations include a German–Chinese A1/A2 reference prompt, no implemented API provider,
no CSV adjudication UI, no benchmark corpus, and no proof of semantic correctness from structural
PASS. Copyright and privacy review remain release-owner responsibilities for newly added data.

## Repository map

- `src/lexicon_pipeline/`: CLI, providers, recovery, validation, merge, reporting, evaluation.
- `prompts/`: canonical generation/review prompts and immutable version snapshots.
- `schemas/`: JSON Schema contracts for records, manifests, and evaluations.
- `examples/`: original synthetic input, examples, and MockProvider configuration.
- `tests/`: offline tests and labeled synthetic fixtures.
- `docs/`: architecture, operations, schema, evaluation, security, and case study.
- `.github/workflows/`: offline CI and MkDocs Pages build/deploy definitions.
- `AGENTS.md` and `NEXT_AGENT_PROMPT.md`: non-shortcut, goal/subagent-aware production handoff.

Start with [docs/PIPELINE_GUIDE.md](docs/PIPELINE_GUIDE.md) for operations and
[PUBLIC_DATA_POLICY.md](PUBLIC_DATA_POLICY.md) before adding any data.

## Citation

No archival DOI or release exists yet. After publication, cite the repository URL, commit SHA,
prompt version, provider/model configuration, and access date. Do not cite the private 4,812-entry
case-study data as publicly available.
