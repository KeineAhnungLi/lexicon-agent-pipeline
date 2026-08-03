from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from lexicon_pipeline.config import ProjectConfig, load_config


@pytest.fixture()
def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture()
def temp_config(tmp_path: Path, repository_root: Path) -> ProjectConfig:
    for directory in ("examples", "prompts", "schemas"):
        shutil.copytree(repository_root / directory, tmp_path / directory)
    fixture_dir = tmp_path / "tests" / "fixtures" / "mock"
    fixture_dir.parent.mkdir(parents=True)
    shutil.copytree(repository_root / "tests" / "fixtures" / "mock", fixture_dir)
    config_path = tmp_path / "project.json"
    data = {
        "project_name": "test_project",
        "repository_root": ".",
        "input_file": "examples/words.demo.tsv",
        "workspace": "workspace",
        "output_dir": "outputs",
        "prompt_template": "prompts/prompt_template.md",
        "review_prompt_template": "prompts/review_prompt_template.md",
        "generation_spec": "prompts/generation_spec.md",
        "examples": "examples/public_examples.jsonl",
        "schema_file": "schemas/lexicon_record.schema.json",
        "batch_size": 15,
        "start_index": 1,
        "final_filename": "test.ai-reviewed.jsonl",
        "expected_fields": 30,
        "provider": "mock",
        "provider_options": {
            "max_validation_attempts": 2,
            "generation_fixture": "tests/fixtures/mock/generated.jsonl",
            "review_fixture": "tests/fixtures/mock/reviewed.jsonl",
        },
    }
    config_path.write_text(json.dumps(data), encoding="utf-8")
    return load_config(config_path)
