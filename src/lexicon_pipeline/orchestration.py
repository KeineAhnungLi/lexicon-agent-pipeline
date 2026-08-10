from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from lexicon_pipeline.config import ProjectConfig
from lexicon_pipeline.errors import ValidationFailure
from lexicon_pipeline.io_utils import atomic_write_json, atomic_write_text, sha256_file
from lexicon_pipeline.manifest import batch_stem, read_manifest, save_manifest
from lexicon_pipeline.providers import create_provider
from lexicon_pipeline.providers.base import AgentProvider, AgentRunResult
from lexicon_pipeline.recovery import determine_next_action, output_paths
from lexicon_pipeline.rendering import render_review_prompt
from lexicon_pipeline.validation import validate_jsonl

RunMode = Literal["full", "generation-only", "review-only"]


def _record_provenance(
    config: ProjectConfig,
    batch: dict[str, Any],
    stage: str,
    artifact: Path,
    provider: str,
    model: str | None,
) -> None:
    path = config.reports_dir / f"{batch_stem(int(batch['id']))}.{stage}.provenance.json"
    atomic_write_json(
        path,
        {
            "batch_id": int(batch["id"]),
            "run_id": str(uuid4()),
            "stage": stage,
            "provider": provider,
            "model": model,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt_version": "1.0.0",
            "prompt_sha256": sha256_file(config.prompt_template),
            "review_prompt_sha256": sha256_file(config.review_prompt_template),
            "generation_spec_sha256": sha256_file(config.generation_spec),
            "examples_sha256": sha256_file(config.examples_file),
            "schema_sha256": sha256_file(config.schema_file),
            "config_sha256": sha256_file(config.config_path),
            "artifact": artifact.name,
            "artifact_sha256": sha256_file(artifact),
            "synthetic_demo": provider == "mock",
        },
    )


def _expected_pos(batch: dict[str, Any]) -> list[str] | None:
    raw = batch.get("expected_pos")
    if not isinstance(raw, list):
        return None
    values = [str(value) for value in raw]
    return values if any(value.strip() for value in values) else None


def _validate_or_raise(path: Path, batch: dict[str, Any]) -> None:
    report = validate_jsonl(
        path,
        expected_words=[str(word) for word in batch["words"]],
        expected_first=int(batch["start"]),
        expected_pos=_expected_pos(batch),
    )
    if not report.valid:
        messages = "; ".join(f"{item.code}: {item.message}" for item in report.issues[:8])
        raise ValidationFailure(f"{path.name} failed validation: {messages}")


def _run_stage_with_repairs(
    config: ProjectConfig,
    provider: AgentProvider,
    batch: dict[str, Any],
    *,
    stage: str,
    prompt: str,
    output: Path,
) -> AgentRunResult:
    max_attempts = int(config.provider_options.get("max_validation_attempts", 2))
    if max_attempts < 1:
        max_attempts = 1
    current_prompt = prompt
    last_error: ValidationFailure | None = None
    for attempt in range(1, max_attempts + 1):
        transcript = (
            config.transcripts_dir
            / f"{batch_stem(int(batch['id']))}.{stage}.attempt_{attempt}.json"
        )
        result = provider.run(
            stage=stage,
            prompt=current_prompt,
            output_path=output,
            transcript_path=transcript,
        )
        try:
            _validate_or_raise(output, batch)
            return result
        except ValidationFailure as exc:
            last_error = exc
            current_prompt = (
                f"{prompt}\n\nThe previous artifact failed mechanical validation:\n{exc}\n"
                "Read every record again, repair the complete artifact, overwrite the requested "
                "output path, and validate before finishing."
            )
    assert last_error is not None
    raise last_error


def run_pipeline(
    config: ProjectConfig,
    *,
    mode: RunMode = "full",
    selected_batch: int | None = None,
    start_batch: int | None = None,
) -> dict[str, Any]:
    manifest = read_manifest(config.manifest_path)
    provider = create_provider(config)
    for batch in manifest["batches"]:
        batch_id = int(batch["id"])
        if start_batch is not None and batch_id < start_batch:
            continue
        if selected_batch is not None and batch_id != selected_batch:
            continue
        generated, reviewed = output_paths(config, batch_id)
        action = determine_next_action(config, batch)
        if action == "complete":
            batch["state"] = "reviewed"
            continue
        if mode == "review-only" and action == "generate":
            batch["state"] = "failed"
            batch["last_error"] = "review-only requested but no valid generated artifact exists"
            save_manifest(config.manifest_path, manifest)
            raise ValidationFailure(str(batch["last_error"]))
        try:
            if action == "generate" and mode != "review-only":
                prompt_path = config.prompts_dir / f"{batch_stem(batch_id)}.prompt.txt"
                prompt = prompt_path.read_text(encoding="utf-8")
                result = _run_stage_with_repairs(
                    config,
                    provider,
                    batch,
                    stage="generation",
                    prompt=prompt,
                    output=generated,
                )
                _record_provenance(
                    config, batch, "generation", generated, result.provider, result.model
                )
                batch["state"] = "generated"
                batch["attempts"] = int(batch["attempts"]) + 1
                batch["last_error"] = None
                save_manifest(config.manifest_path, manifest)
                action = "review"
            if mode == "generation-only":
                continue
            if action == "review":
                review_prompt = render_review_prompt(config, batch, generated, reviewed)
                review_prompt_path = (
                    config.prompts_dir / f"{batch_stem(batch_id)}.review.prompt.txt"
                )
                atomic_write_text(review_prompt_path, review_prompt)
                result = _run_stage_with_repairs(
                    config,
                    provider,
                    batch,
                    stage="review",
                    prompt=review_prompt,
                    output=reviewed,
                )
                _record_provenance(
                    config, batch, "review", reviewed, result.provider, result.model
                )
                batch["state"] = "reviewed"
                batch["attempts"] = int(batch["attempts"]) + 1
                batch["last_error"] = None
                summary_path = (
                    config.reports_dir / f"{batch_stem(batch_id)}.review_summary.md"
                )
                if not summary_path.is_file():
                    atomic_write_text(
                        summary_path,
                        "\n".join(
                        [
                            f"# Review summary — {batch_stem(batch_id)}",
                            "",
                            f"- Independent provider invocation: `{result.provider}`",
                            f"- Reviewed rows: {len(batch['words'])}",
                            "- Mechanical validation: PASS",
                            "- Human linguistic verification: not performed",
                            "",
                            "This operational summary records completion, not semantic accuracy.",
                            "",
                        ]
                        ),
                    )
                save_manifest(config.manifest_path, manifest)
        except Exception as exc:
            batch["state"] = "failed"
            batch["last_error"] = f"{type(exc).__name__}: {exc}"
            save_manifest(config.manifest_path, manifest)
            raise
    return manifest
