from __future__ import annotations

from pathlib import Path
from typing import Any

from lexicon_pipeline.config import ProjectConfig
from lexicon_pipeline.errors import StateError
from lexicon_pipeline.io_utils import atomic_write_text
from lexicon_pipeline.manifest import batch_stem, read_manifest, save_manifest


def render_text(
    template: str,
    batch: dict[str, Any],
    *,
    generation_spec: str = "",
    examples: str = "",
    require_content_placeholders: bool = False,
) -> str:
    positions = batch.get("expected_pos", [""] * len(batch["words"]))
    words = "\n".join(
        (
            f"{index}. {word}"
            + (f"\t[expected_pos={pos}]" if str(pos).strip() else "")
        )
        for index, (word, pos) in enumerate(
            zip(batch["words"], positions, strict=True),
            start=int(batch["start"]),
        )
    )
    values = {
        "{{BATCH_ID}}": batch_stem(int(batch["id"])),
        "{{START_INDEX}}": str(batch["start"]),
        "{{END_INDEX}}": str(batch["end"]),
        "{{WORD_LIST}}": words,
        "{{GENERATION_SPEC}}": generation_spec,
        "{{EXAMPLES}}": examples,
    }
    if require_content_placeholders:
        required = ("{{WORD_LIST}}", "{{GENERATION_SPEC}}", "{{EXAMPLES}}", "{{START_INDEX}}")
        missing = [marker for marker in required if marker not in template]
        if missing:
            raise StateError(f"prompt template is missing required placeholders: {missing}")
    rendered = template
    for marker, value in values.items():
        rendered = rendered.replace(marker, value)
    unresolved = [marker for marker in values if marker in rendered]
    if unresolved:
        raise StateError(f"unresolved prompt placeholders: {unresolved}")
    return rendered


def render_prompts(config: ProjectConfig) -> list[Path]:
    manifest = read_manifest(config.manifest_path)
    template = config.prompt_template.read_text(encoding="utf-8")
    generation_spec = config.generation_spec.read_text(encoding="utf-8")
    examples = config.examples_file.read_text(encoding="utf-8")
    paths: list[Path] = []
    for batch in manifest["batches"]:
        path = config.prompts_dir / f"{batch_stem(int(batch['id']))}.prompt.txt"
        atomic_write_text(
            path,
            render_text(
                template,
                batch,
                generation_spec=generation_spec,
                examples=examples,
                require_content_placeholders=True,
            ),
        )
        if batch["state"] == "prepared":
            batch["state"] = "rendered"
        paths.append(path)
    save_manifest(config.manifest_path, manifest)
    return paths


def render_review_prompt(
    config: ProjectConfig,
    batch: dict[str, Any],
    draft: Path,
    output: Path,
) -> str:
    template = config.review_prompt_template.read_text(encoding="utf-8")
    prompt = render_text(template, batch)
    values = {
        "{{DRAFT_PATH}}": str(draft),
        "{{GENERATION_PROMPT_PATH}}": str(
            config.prompts_dir / f"{batch_stem(int(batch['id']))}.prompt.txt"
        ),
        "{{OUTPUT_PATH}}": str(output),
        "{{SUMMARY_PATH}}": str(
            config.reports_dir / f"{batch_stem(int(batch['id']))}.review_summary.md"
        ),
        "{{VALIDATION_COMMAND}}": (
            "lexicon-pipeline --config "
            f'"{config.config_path}" validate --batch {batch["id"]} --stage reviewed'
        ),
    }
    for marker, value in values.items():
        prompt = prompt.replace(marker, value)
    return prompt
