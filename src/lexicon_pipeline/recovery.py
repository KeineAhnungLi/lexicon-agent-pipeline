from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from lexicon_pipeline.config import ProjectConfig
from lexicon_pipeline.manifest import batch_stem
from lexicon_pipeline.validation import validate_jsonl

NextAction = Literal["generate", "review", "complete"]


def output_paths(config: ProjectConfig, batch_id: int) -> tuple[Path, Path]:
    stem = batch_stem(batch_id)
    return (
        config.outputs_dir / f"{stem}.generated.jsonl",
        config.outputs_dir / f"{stem}.reviewed.jsonl",
    )


def determine_next_action(config: ProjectConfig, batch: dict[str, Any]) -> NextAction:
    words = [str(word) for word in batch["words"]]
    start = int(batch["start"])
    generated, reviewed = output_paths(config, int(batch["id"]))
    if reviewed.is_file() and validate_jsonl(
        reviewed, expected_words=words, expected_first=start
    ).valid:
        return "complete"
    if generated.is_file() and validate_jsonl(
        generated, expected_words=words, expected_first=start
    ).valid:
        return "review"
    return "generate"
