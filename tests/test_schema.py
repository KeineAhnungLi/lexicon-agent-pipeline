from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from lexicon_pipeline.config import ProjectConfig
from lexicon_pipeline.io_utils import sha256_file
from lexicon_pipeline.prepare import prepare_workspace


def test_all_schemas_are_well_formed(repository_root: Path) -> None:
    for path in (repository_root / "schemas").glob("*.schema.json"):
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def test_public_examples_pass_json_schema(repository_root: Path) -> None:
    schema = json.loads(
        (repository_root / "schemas" / "lexicon_agent_record.schema.json").read_text(
            encoding="utf-8"
        )
    )
    validator = Draft202012Validator(schema)
    rows = (
        repository_root / "examples" / "public_examples.jsonl"
    ).read_text(encoding="utf-8").splitlines()
    assert not [
        error
        for line in rows
        for error in validator.iter_errors(json.loads(line))
    ]


def test_generated_manifest_passes_schema(
    temp_config: ProjectConfig, repository_root: Path
) -> None:
    manifest = prepare_workspace(temp_config)
    schema = json.loads(
        (repository_root / "schemas" / "manifest.schema.json").read_text(encoding="utf-8")
    )
    assert not list(Draft202012Validator(schema).iter_errors(manifest))


def test_prompt_snapshot_hashes_match(repository_root: Path) -> None:
    version = repository_root / "prompts" / "versions" / "v2.0.0"
    manifest = json.loads((version / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "2.0.0"
    assert set(manifest["files"]) == {
        "prompt_template.md",
        "review_prompt_template.md",
        "generation_spec.md",
    }
    for filename, digest in manifest["files"].items():
        assert sha256_file(version / filename) == digest
        assert (version / filename).read_bytes() == (
            repository_root / "prompts" / filename
        ).read_bytes()
