from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from lexicon_pipeline.config import ProjectConfig
from lexicon_pipeline.io_utils import atomic_write_json, atomic_write_text, load_json, sha256_file
from lexicon_pipeline.manifest import batch_stem, read_manifest
from lexicon_pipeline.providers.codex_cli import parse_tokens_used
from lexicon_pipeline.recovery import output_paths
from lexicon_pipeline.validation import validate_jsonl

ReportStage = Literal["generated", "reviewed"]


def _token_attempts(config: ProjectConfig, stem: str, stage: ReportStage) -> list[dict[str, Any]]:
    attempts: list[dict[str, Any]] = []
    included_stages = ("generation",) if stage == "generated" else ("generation", "review")
    for stage_name in included_stages:
        pattern = f"{stem}.{stage_name}.attempt_*.json"
        for path in sorted(config.transcripts_dir.glob(pattern)):
            tokens: int | None = None
            try:
                data = load_json(path)
                raw_tokens = data.get("tokens_used") if isinstance(data, dict) else None
                if isinstance(raw_tokens, int) and raw_tokens >= 0:
                    tokens = raw_tokens
                elif isinstance(data, dict):
                    tokens = parse_tokens_used(
                        str(data.get("stdout", "")), str(data.get("stderr", ""))
                    )
            except (OSError, ValueError):
                pass
            attempts.append(
                {"stage": stage_name, "transcript": path.name, "tokens_used": tokens}
            )
    return attempts


def build_quality_report(
    config: ProjectConfig, *, stage: ReportStage = "reviewed"
) -> tuple[Path, Path, dict[str, Any]]:
    manifest = read_manifest(config.manifest_path)
    batches: list[dict[str, Any]] = []
    total = 0
    known_tokens_total = 0
    exact_attempts = 0
    missing_attempts = 0
    for batch in manifest["batches"]:
        stem = batch_stem(int(batch["id"]))
        generated, reviewed = output_paths(config, int(batch["id"]))
        artifact = generated if stage == "generated" else reviewed
        report = validate_jsonl(
            artifact,
            expected_words=[str(word) for word in batch["words"]],
            expected_first=int(batch["start"]),
            expected_pos=[str(value) for value in batch.get("expected_pos", [])] or None,
            schema="agent",
        )
        total += report.row_count if report.valid else 0
        generation_provenance = config.reports_dir / f"{stem}.generation.provenance.json"
        review_provenance = config.reports_dir / f"{stem}.review.provenance.json"
        generation_data = (
            load_json(generation_provenance) if generation_provenance.is_file() else {}
        )
        review_data = load_json(review_provenance) if review_provenance.is_file() else {}
        token_attempts = _token_attempts(config, stem, stage)
        known = [
            int(item["tokens_used"])
            for item in token_attempts
            if isinstance(item["tokens_used"], int)
        ]
        known_tokens_total += sum(known)
        exact_attempts += len(known)
        missing_attempts += len(token_attempts) - len(known)
        batch_tokens = sum(known) if token_attempts and len(known) == len(token_attempts) else None
        batches.append(
            {
                "id": batch["id"],
                "state": batch["state"],
                "valid": report.valid,
                "rows": report.row_count,
                "artifact_sha256": sha256_file(artifact) if artifact.is_file() else None,
                "issues": [issue.__dict__ for issue in report.issues],
                "generation_run_id": generation_data.get("run_id"),
                "review_run_id": review_data.get("run_id"),
                "tokens_used": batch_tokens,
                "token_attempts": token_attempts,
            }
        )
    final_output = config.output_dir / config.final_filename
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prompt_version": "2.0.0",
        "prompt_sha256": sha256_file(config.prompt_template),
        "review_prompt_sha256": sha256_file(config.review_prompt_template),
        "generation_spec_sha256": sha256_file(config.generation_spec),
        "examples_sha256": sha256_file(config.examples_file),
        "agent_schema_sha256": sha256_file(config.agent_schema_file),
        "final_schema_sha256": sha256_file(config.schema_file),
        "config_sha256": sha256_file(config.config_path),
        "input_sha256": sha256_file(config.words_file),
        "provider": config.provider,
        "provider_model": config.provider_options.get("model") or "host default / not reported",
        "provider_reasoning_effort": config.provider_options.get("reasoning_effort"),
        "artifact_stage": stage,
        "independent_review_performed": stage == "reviewed",
        "mechanical_validation_passed": all(item["valid"] for item in batches),
        "linguistic_accuracy_verified": False,
        "notice": (
            "Mechanical validation does not establish semantic, grammatical, or translation "
            "accuracy. Human evaluation is required."
        ),
        "valid_rows": total,
        "valid_reviewed_rows": total if stage == "reviewed" else 0,
        "known_tokens_total": known_tokens_total,
        "exact_token_attempts": exact_attempts,
        "missing_token_attempts": missing_attempts,
        "batch_count": len(batches),
        "final_output": final_output.name if final_output.is_file() else None,
        "final_output_sha256": sha256_file(final_output) if final_output.is_file() else None,
        "known_human_sampling_exceptions": [],
        "batches": batches,
    }
    if stage == "reviewed":
        json_path = config.output_dir / "quality_report.json"
        md_path = config.output_dir / "QUALITY_REPORT.md"
    else:
        json_path = config.output_dir / "quality_report.generated.json"
        md_path = config.output_dir / "QUALITY_REPORT.generated.md"
    atomic_write_json(json_path, data)
    lines: list[str] = [
        "# Quality report",
        "",
        f"- Generated: {data['generated_at']}",
        f"- Provider: `{config.provider}`",
        f"- Prompt version: `{data['prompt_version']}`",
        f"- Artifact stage: `{stage}`",
        f"- Valid rows: {total}",
        f"- Independent review performed: **{'Yes' if stage == 'reviewed' else 'No'}**",
        f"- Exact known tokens: {known_tokens_total} ({exact_attempts} attempts)",
        f"- Attempts with missing token usage: {missing_attempts}",
        f"- Final output SHA-256: `{data['final_output_sha256']}`",
        f"- Mechanical validation: {'PASS' if data['mechanical_validation_passed'] else 'FAIL'}",
        "- Linguistic accuracy verified: **No**",
        "",
        str(data["notice"]),
        "",
        "| Batch | State | Valid | Rows | Tokens | Generation run | Review run |",
        "|---:|---|:---:|---:|---:|---|---|",
    ]
    lines.extend(
        f"| {item['id']} | {item['state']} | {'yes' if item['valid'] else 'no'} | "
        f"{item['rows']} | {item['tokens_used']} | `{item['generation_run_id']}` | "
        f"`{item['review_run_id']}` |"
        for item in batches
    )
    atomic_write_text(md_path, "\n".join(lines) + "\n")
    return json_path, md_path, data
