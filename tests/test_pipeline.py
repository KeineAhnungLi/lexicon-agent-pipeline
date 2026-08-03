from __future__ import annotations

import pytest

from lexicon_pipeline.config import ProjectConfig
from lexicon_pipeline.errors import ConfigurationError, StateError, ValidationFailure
from lexicon_pipeline.manifest import read_manifest
from lexicon_pipeline.merging import merge_reviewed
from lexicon_pipeline.orchestration import run_pipeline
from lexicon_pipeline.prepare import prepare_workspace
from lexicon_pipeline.recovery import determine_next_action
from lexicon_pipeline.rendering import render_prompts
from lexicon_pipeline.reporting import build_quality_report


def test_prepare_render_run_merge_report(temp_config: ProjectConfig) -> None:
    manifest = prepare_workspace(temp_config)
    assert len(manifest["batches"]) == 1
    assert len(render_prompts(temp_config)) == 1
    run_pipeline(temp_config)
    merged, count = merge_reviewed(temp_config)
    assert count == 15
    assert merged.is_file()
    _, _, report = build_quality_report(temp_config)
    assert report["mechanical_validation_passed"] is True
    assert report["linguistic_accuracy_verified"] is False


def test_prepare_refuses_nonempty_workspace(temp_config: ProjectConfig) -> None:
    prepare_workspace(temp_config)
    with pytest.raises(ConfigurationError, match="not empty"):
        prepare_workspace(temp_config)


def test_force_reset_requires_confirmation(temp_config: ProjectConfig) -> None:
    prepare_workspace(temp_config)
    with pytest.raises(ConfigurationError, match="requires --yes"):
        prepare_workspace(temp_config, force_reset=True)


def test_merge_refuses_generated_only(temp_config: ProjectConfig) -> None:
    prepare_workspace(temp_config)
    render_prompts(temp_config)
    run_pipeline(temp_config, mode="generation-only")
    with pytest.raises(StateError, match="refusing merge"):
        merge_reviewed(temp_config)


def test_generated_only_resumes_at_review(temp_config: ProjectConfig) -> None:
    prepare_workspace(temp_config)
    render_prompts(temp_config)
    run_pipeline(temp_config, mode="generation-only")
    manifest = read_manifest(temp_config.manifest_path)
    batch = manifest["batches"][0]
    assert determine_next_action(temp_config, batch) == "review"
    run_pipeline(temp_config, mode="review-only")
    assert read_manifest(temp_config.manifest_path)["batches"][0]["state"] == "reviewed"


def test_review_only_requires_draft(temp_config: ProjectConfig) -> None:
    prepare_workspace(temp_config)
    render_prompts(temp_config)
    with pytest.raises(ValidationFailure, match="no valid generated"):
        run_pipeline(temp_config, mode="review-only")


def test_completed_batch_is_idempotently_skipped(temp_config: ProjectConfig) -> None:
    prepare_workspace(temp_config)
    render_prompts(temp_config)
    run_pipeline(temp_config)
    before = read_manifest(temp_config.manifest_path)["batches"][0]["attempts"]
    run_pipeline(temp_config)
    after = read_manifest(temp_config.manifest_path)["batches"][0]["attempts"]
    assert before == after == 2


def test_merge_refuses_to_overwrite_final_output(temp_config: ProjectConfig) -> None:
    prepare_workspace(temp_config)
    render_prompts(temp_config)
    run_pipeline(temp_config)
    merge_reviewed(temp_config)
    with pytest.raises(StateError, match="refusing overwrite"):
        merge_reviewed(temp_config)


def test_review_summary_and_hash_provenance_exist(temp_config: ProjectConfig) -> None:
    prepare_workspace(temp_config)
    render_prompts(temp_config)
    run_pipeline(temp_config)
    summary = temp_config.reports_dir / "batch_01.review_summary.md"
    provenance = temp_config.reports_dir / "batch_01.review.provenance.json"
    assert summary.is_file()
    assert provenance.is_file()
    assert "semantic accuracy" in summary.read_text(encoding="utf-8")
