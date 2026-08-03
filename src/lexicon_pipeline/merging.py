from __future__ import annotations

from pathlib import Path
from typing import Any

from lexicon_pipeline.config import ProjectConfig
from lexicon_pipeline.errors import StateError
from lexicon_pipeline.io_utils import atomic_write_jsonl, sha256_file
from lexicon_pipeline.manifest import read_manifest
from lexicon_pipeline.recovery import output_paths
from lexicon_pipeline.validation import read_jsonl, validate_jsonl


def merge_reviewed(
    config: ProjectConfig,
    output: Path | None = None,
    *,
    overwrite: bool = False,
) -> tuple[Path, int]:
    manifest = read_manifest(config.manifest_path)
    rows: list[dict[str, Any]] = []
    for batch in manifest["batches"]:
        batch_id = int(batch["id"])
        _, reviewed = output_paths(config, batch_id)
        report = validate_jsonl(
            reviewed,
            expected_words=[str(word) for word in batch["words"]],
            expected_first=int(batch["start"]),
        )
        if not report.valid or batch["state"] != "reviewed":
            raise StateError(f"batch {batch_id} is not valid and reviewed; refusing merge")
        batch_rows, parse_issues = read_jsonl(reviewed)
        if parse_issues:
            raise StateError(f"batch {batch_id} has parse issues; refusing merge")
        rows.extend(batch_rows)
    target = output or (config.output_dir / config.final_filename)
    if target.exists() and not overwrite:
        raise StateError(f"output already exists; refusing overwrite: {target}")
    atomic_write_jsonl(target, rows)
    final_report = validate_jsonl(
        target,
        expected_words=[str(word) for batch in manifest["batches"] for word in batch["words"]],
        expected_first=1,
    )
    if not final_report.valid:
        target.unlink(missing_ok=True)
        raise StateError("merged output failed global validation")
    return target, len(rows)


def merged_digest(path: Path) -> str:
    return sha256_file(path)
