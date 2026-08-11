from __future__ import annotations

import json
from dataclasses import replace
from typing import Any

import pytest

from lexicon_pipeline.cli import _parser
from lexicon_pipeline.config import ProjectConfig
from lexicon_pipeline.constants import AGENT_FIELD_NAMES, FINAL_FIELD_NAMES, MISSING_VALUE
from lexicon_pipeline.errors import StateError
from lexicon_pipeline.io_utils import atomic_write_jsonl
from lexicon_pipeline.manifest import read_manifest, save_manifest
from lexicon_pipeline.merging import merge_batches
from lexicon_pipeline.prepare import prepare_workspace
from lexicon_pipeline.reporting import build_quality_report


def _agent_row(first: int, word: str) -> dict[str, Any]:
    values: dict[str, Any] = {field: MISSING_VALUE for field in AGENT_FIELD_NAMES}
    values.update(
        {
            "first": first,
            "word": word,
            "spell_word": word,
            "class_options": "N.",
            "class": "N.",
            "correct_option": "N. synthetic meaning",
            "meaning1": "n. synthetic meaning",
            "meaning2": "n. second meaning",
        }
    )
    return values


def _write_stage(config: ProjectConfig, stage: str) -> list[dict[str, Any]]:
    manifest = read_manifest(config.manifest_path)
    rows: list[dict[str, Any]] = []
    for batch in manifest["batches"]:
        batch_rows = [
            _agent_row(int(batch["start"]) + offset, str(word))
            for offset, word in enumerate(batch["words"])
        ]
        suffix = "generated" if stage == "generated" else "reviewed"
        atomic_write_jsonl(
            config.outputs_dir / f"batch_{int(batch['id']):02d}.{suffix}.jsonl",
            batch_rows,
        )
        batch["state"] = stage
        rows.extend(batch_rows)
    save_manifest(config.manifest_path, manifest)
    return rows


def test_generated_merge_derives_final_schema_and_uses_config_start_index(
    temp_config: ProjectConfig,
) -> None:
    config = replace(temp_config, start_index=1001)
    prepare_workspace(config)
    source_rows = _write_stage(config, "generated")

    merged, count = merge_batches(config, stage="generated")

    assert count == len(source_rows)
    rows = [json.loads(line) for line in merged.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["first"] == 1001
    assert tuple(rows[0]) == FINAL_FIELD_NAMES
    assert rows[0]["meaning_merged"] == "n. synthetic meaning；n. second meaning"


def test_default_reviewed_merge_still_rejects_generated_only(
    temp_config: ProjectConfig,
) -> None:
    prepare_workspace(temp_config)
    _write_stage(temp_config, "generated")

    with pytest.raises(StateError, match="reviewed"):
        merge_batches(temp_config)


def test_default_merge_derives_final_records_from_reviewed_artifact(
    temp_config: ProjectConfig,
) -> None:
    prepare_workspace(temp_config)
    reviewed = _write_stage(temp_config, "reviewed")

    merged, count = merge_batches(temp_config)

    rows = [json.loads(line) for line in merged.read_text(encoding="utf-8").splitlines()]
    assert count == len(reviewed)
    assert rows[0]["meaning_merged"] == "n. synthetic meaning；n. second meaning"


def test_report_stage_sums_exact_transcript_tokens_and_preserves_missing(
    temp_config: ProjectConfig,
) -> None:
    prepare_workspace(temp_config)
    _write_stage(temp_config, "generated")
    first = temp_config.transcripts_dir / "batch_01.generation.attempt_1.json"
    second = temp_config.transcripts_dir / "batch_01.generation.attempt_2.json"
    first.write_text(json.dumps({"tokens_used": 1234}), encoding="utf-8")
    second.write_text(
        json.dumps({"stdout": "finished", "stderr": "token footer unavailable"}),
        encoding="utf-8",
    )

    _, _, report = build_quality_report(temp_config, stage="generated")

    assert report["artifact_stage"] == "generated"
    assert report["independent_review_performed"] is False
    assert report["known_tokens_total"] == 1234
    assert report["exact_token_attempts"] == 1
    assert report["missing_token_attempts"] == 1
    assert report["batches"][0]["tokens_used"] is None
    assert report["batches"][0]["token_attempts"][1]["tokens_used"] is None


def test_report_extracts_tokens_from_legacy_transcript_text(
    temp_config: ProjectConfig,
) -> None:
    prepare_workspace(temp_config)
    _write_stage(temp_config, "generated")
    transcript = temp_config.transcripts_dir / "batch_01.generation.attempt_1.json"
    transcript.write_text(
        json.dumps({"stdout": "", "stderr": "tokens used\r\n1,705"}),
        encoding="utf-8",
    )

    _, _, report = build_quality_report(temp_config, stage="generated")

    assert report["known_tokens_total"] == 1705
    assert report["batches"][0]["tokens_used"] == 1705


def test_cli_stage_defaults_are_reviewed_and_generated_is_explicit() -> None:
    parser = _parser()

    assert parser.parse_args(["merge"]).stage == "reviewed"
    assert parser.parse_args(["report"]).stage == "reviewed"
    assert parser.parse_args(["merge", "--stage", "generated"]).stage == "generated"
    assert parser.parse_args(["report", "--stage", "generated"]).stage == "generated"
