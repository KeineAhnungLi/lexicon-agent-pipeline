# Contributing

Code, prompt, and documentation contributions are accepted under MIT. Contributions to the public
synthetic examples, demo word list, or MockProvider fixtures are accepted under CC0-1.0. Submitters
must have the right to grant the applicable license.

For local review:

1. Create a branch and keep private data outside the repository.
2. Add typed code and offline tests for behavior changes.
3. Do not add semantic shortcuts to orchestration code.
4. Version prompt or schema behavior changes and update their changelogs.
5. Run `ruff check .`, `mypy`, `pytest`, the MockProvider demo, schema validation, MkDocs strict
   build, and the public-release audit.
6. Explain data provenance and rights for any fixture change.

Generated-only artifacts are never final. Changes that weaken independent review, reviewed-only
merge, path safety, atomic writes, provenance, or disclosure boundaries should be rejected.
