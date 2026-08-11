from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from lexicon_pipeline.config import ProjectConfig
from lexicon_pipeline.io_utils import atomic_write_json, load_json, sha256_file


def new_manifest(
    config: ProjectConfig,
    words: list[str],
    *,
    expected_pos: list[str] | None = None,
) -> dict[str, Any]:
    if expected_pos is not None and len(expected_pos) != len(words):
        raise ValueError("expected_pos must align one-to-one with words")
    positions = expected_pos if expected_pos is not None else [""] * len(words)
    batches: list[dict[str, Any]] = []
    for number, offset in enumerate(range(0, len(words), config.batch_size), start=1):
        batch_words = words[offset : offset + config.batch_size]
        batch_pos = positions[offset : offset + config.batch_size]
        batches.append(
            {
                "id": number,
                "start": config.start_index + offset,
                "end": config.start_index + offset + len(batch_words) - 1,
                "words": batch_words,
                "expected_pos": batch_pos,
                "state": "prepared",
                "attempts": 0,
                "last_error": None,
            }
        )
    return {
        "manifest_version": 2,
        "contract_version": "2.0.0",
        "project": config.project_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "batch_size": config.batch_size,
        "prompt_version": "2.0.0",
        "config_hash": sha256_file(config.config_path),
        "prompt_hash": sha256_file(config.prompt_template),
        "review_prompt_hash": sha256_file(config.review_prompt_template),
        "generation_spec_hash": sha256_file(config.generation_spec),
        "examples_hash": sha256_file(config.examples_file),
        "agent_schema_hash": sha256_file(config.agent_schema_file),
        "final_schema_hash": sha256_file(config.schema_file),
        "input_hash": sha256_file(config.words_file),
        "batches": batches,
    }


def read_manifest(path: Path) -> dict[str, Any]:
    value = load_json(path)
    if not isinstance(value, dict) or not isinstance(value.get("batches"), list):
        raise ValueError(f"invalid manifest: {path}")
    if value.get("manifest_version") != 2 or value.get("contract_version") != "2.0.0":
        raise ValueError(
            "incompatible manifest contract; run prepare again with a fresh workspace"
        )
    return cast(dict[str, Any], value)


def save_manifest(path: Path, manifest: Mapping[str, Any]) -> None:
    atomic_write_json(path, manifest)


def find_batch(manifest: dict[str, Any], batch_id: int) -> dict[str, Any]:
    for item in manifest["batches"]:
        if isinstance(item, dict) and item.get("id") == batch_id:
            return item
    raise KeyError(f"batch {batch_id} is absent from manifest")


def batch_stem(batch_id: int) -> str:
    return f"batch_{batch_id:02d}"
