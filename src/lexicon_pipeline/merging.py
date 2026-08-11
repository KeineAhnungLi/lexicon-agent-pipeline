from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from lexicon_pipeline.config import ProjectConfig
from lexicon_pipeline.errors import StateError
from lexicon_pipeline.io_utils import atomic_write_jsonl, sha256_file
from lexicon_pipeline.manifest import read_manifest
from lexicon_pipeline.recovery import output_paths
from lexicon_pipeline.validation import (
    read_jsonl,
    validate_jsonl,
    with_derived_meaning_merged,
)

MergeStage = Literal["generated", "reviewed"]


def merge_batches(
    config: ProjectConfig,
    output: Path | None = None,
    *,
    stage: MergeStage = "reviewed",
    overwrite: bool = False,
) -> tuple[Path, int]:
    manifest = read_manifest(config.manifest_path)
    rows: list[dict[str, Any]] = []
    for batch in manifest["batches"]:
        batch_id = int(batch["id"])
        generated, reviewed = output_paths(config, batch_id)
        artifact = generated if stage == "generated" else reviewed
        report = validate_jsonl(
            artifact,
            expected_words=[str(word) for word in batch["words"]],
            expected_first=int(batch["start"]),
            expected_pos=[str(value) for value in batch.get("expected_pos", [])] or None,
            schema="agent",
        )
        allowed_states = {"generated", "reviewed"} if stage == "generated" else {"reviewed"}
        if not report.valid or batch["state"] not in allowed_states:
            raise StateError(
                f"batch {batch_id} is not valid and {stage}; refusing merge"
            )
        batch_rows, parse_issues = read_jsonl(artifact)
        if parse_issues:
            raise StateError(f"batch {batch_id} has parse issues; refusing merge")
        rows.extend(with_derived_meaning_merged(row) for row in batch_rows)
    target = output or (config.output_dir / config.final_filename)
    if target.exists() and not overwrite:
        raise StateError(f"output already exists; refusing overwrite: {target}")
    atomic_write_jsonl(target, rows)
    final_report = validate_jsonl(
        target,
        expected_words=[str(word) for batch in manifest["batches"] for word in batch["words"]],
        expected_first=config.start_index,
        expected_pos=[
            str(value)
            for batch in manifest["batches"]
            for value in batch.get("expected_pos", [])
        ] or None,
        schema="final",
    )
    if not final_report.valid:
        target.unlink(missing_ok=True)
        raise StateError("merged output failed global validation")
    return target, len(rows)


def merge_reviewed(
    config: ProjectConfig,
    output: Path | None = None,
    *,
    overwrite: bool = False,
) -> tuple[Path, int]:
    """Backward-compatible reviewed-only merge entry point."""
    return merge_batches(config, output, stage="reviewed", overwrite=overwrite)


def merged_digest(path: Path) -> str:
    return sha256_file(path)
