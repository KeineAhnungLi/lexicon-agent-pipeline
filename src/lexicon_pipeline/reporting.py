from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lexicon_pipeline.config import ProjectConfig
from lexicon_pipeline.io_utils import atomic_write_json, atomic_write_text, load_json, sha256_file
from lexicon_pipeline.manifest import batch_stem, read_manifest
from lexicon_pipeline.recovery import output_paths
from lexicon_pipeline.validation import validate_jsonl


def build_quality_report(config: ProjectConfig) -> tuple[Path, Path, dict[str, Any]]:
    manifest = read_manifest(config.manifest_path)
    batches: list[dict[str, Any]] = []
    total = 0
    for batch in manifest["batches"]:
        stem = batch_stem(int(batch["id"]))
        _, reviewed = output_paths(config, int(batch["id"]))
        report = validate_jsonl(
            reviewed,
            expected_words=[str(word) for word in batch["words"]],
            expected_first=int(batch["start"]),
        )
        total += report.row_count if report.valid else 0
        generation_provenance = config.reports_dir / f"{stem}.generation.provenance.json"
        review_provenance = config.reports_dir / f"{stem}.review.provenance.json"
        generation_data = (
            load_json(generation_provenance) if generation_provenance.is_file() else {}
        )
        review_data = load_json(review_provenance) if review_provenance.is_file() else {}
        batches.append(
            {
                "id": batch["id"],
                "state": batch["state"],
                "valid": report.valid,
                "rows": report.row_count,
                "artifact_sha256": sha256_file(reviewed) if reviewed.is_file() else None,
                "issues": [issue.__dict__ for issue in report.issues],
                "generation_run_id": generation_data.get("run_id"),
                "review_run_id": review_data.get("run_id"),
            }
        )
    final_output = config.output_dir / config.final_filename
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prompt_version": "1.0.0",
        "prompt_sha256": sha256_file(config.prompt_template),
        "review_prompt_sha256": sha256_file(config.review_prompt_template),
        "generation_spec_sha256": sha256_file(config.generation_spec),
        "examples_sha256": sha256_file(config.examples_file),
        "schema_sha256": sha256_file(config.schema_file),
        "config_sha256": sha256_file(config.config_path),
        "input_sha256": sha256_file(config.words_file),
        "provider": config.provider,
        "provider_model": config.provider_options.get("model") or "host default / not reported",
        "mechanical_validation_passed": all(item["valid"] for item in batches),
        "linguistic_accuracy_verified": False,
        "notice": (
            "Mechanical validation does not establish semantic, grammatical, or translation "
            "accuracy. Human evaluation is required."
        ),
        "valid_reviewed_rows": total,
        "batch_count": len(batches),
        "final_output": final_output.name if final_output.is_file() else None,
        "final_output_sha256": sha256_file(final_output) if final_output.is_file() else None,
        "known_human_sampling_exceptions": [],
        "batches": batches,
    }
    json_path = config.output_dir / "quality_report.json"
    md_path = config.output_dir / "QUALITY_REPORT.md"
    atomic_write_json(json_path, data)
    lines = [
        "# Quality report",
        "",
        f"- Generated: {data['generated_at']}",
        f"- Provider: `{config.provider}`",
        f"- Prompt version: `{data['prompt_version']}`",
        f"- Valid reviewed rows: {total}",
        f"- Final output SHA-256: `{data['final_output_sha256']}`",
        f"- Mechanical validation: {'PASS' if data['mechanical_validation_passed'] else 'FAIL'}",
        "- Linguistic accuracy verified: **No**",
        "",
        data["notice"],
        "",
        "| Batch | State | Valid | Rows | Generation run | Review run |",
        "|---:|---|:---:|---:|---|---|",
    ]
    lines.extend(
        f"| {item['id']} | {item['state']} | {'yes' if item['valid'] else 'no'} | "
        f"{item['rows']} | `{item['generation_run_id']}` | `{item['review_run_id']}` |"
        for item in batches
    )
    atomic_write_text(md_path, "\n".join(lines) + "\n")
    return json_path, md_path, data
