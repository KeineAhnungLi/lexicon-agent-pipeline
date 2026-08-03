# Public release audit record

Audit date: 2026-07-30 (Asia/Shanghai)

Operational source-tree audit: **PASS**

Verified locally:

- 38 pytest tests passed;
- deterministic MockProvider demo produced 15 reviewed rows;
- all three JSON Schemas passed Draft 2020-12 meta-validation;
- public examples contain 15 mechanically valid, input-aligned, 30-field records;
- prompt snapshot hashes match the v1.0.0 manifest;
- secret/path/private-artifact/large-file/required-document scan returned no blocking findings;
- no production list, source spreadsheet, historical output, archive, or raw production transcript
  is tracked;
- MIT covers code, prompts, and documentation; CC0-1.0 covers original public synthetic data.

Environment-bounded checks:

- source compilation passed;
- Codex CLI flags used by the provider were checked against the installed CLI help;
- Ruff, mypy, MkDocs, and Docker execution could not be run locally because the tools were absent
  and dependency installation stalled in the current network environment;
- CI is configured to run lint, type checking, all tests/schema checks, demo, release audit, and a
  strict MkDocs build on Python 3.10, 3.11, and 3.12;
- Docker build/run and Pages deployment remain to be exercised in an environment providing Docker
  and dependency registry access.

Release status: **READY FOR PUBLICATION** subject to the environment-bounded CI/Docker/docs checks
running successfully on GitHub Actions after the initial push.
