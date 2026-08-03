from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lexicon_pipeline.errors import ConfigurationError


@dataclass(frozen=True)
class ProjectConfig:
    config_path: Path
    project_root: Path
    project_name: str
    words_file: Path
    workspace: Path
    output_dir: Path
    prompt_template: Path
    review_prompt_template: Path
    generation_spec: Path
    examples_file: Path
    schema_file: Path
    batch_size: int
    start_index: int
    final_filename: str
    provider: str
    provider_options: Mapping[str, Any]
    expected_fields: int = 30

    @property
    def prompts_dir(self) -> Path:
        return self.workspace / "rendered_prompts"

    @property
    def outputs_dir(self) -> Path:
        return self.workspace / "ai_outputs"

    @property
    def reports_dir(self) -> Path:
        return self.workspace / "reports"

    @property
    def transcripts_dir(self) -> Path:
        return self.workspace / "transcripts"

    @property
    def manifest_path(self) -> Path:
        return self.workspace / "manifest.json"


def _resolve(base: Path, raw: str) -> Path:
    return (base / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()


def _mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ConfigurationError(f"{label} must be a JSON object")
    return value


def load_config(
    config_path: Path,
    *,
    workspace_override: Path | None = None,
    provider_override: str | None = None,
    batch_size_override: int | None = None,
) -> ProjectConfig:
    resolved_config = config_path.resolve()
    try:
        raw = json.loads(resolved_config.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"cannot read config {resolved_config}: {exc}") from exc
    data = _mapping(raw, "configuration")
    base = resolved_config.parent
    input_value = data.get("input_file", data.get("words_file"))
    required = (
        "workspace",
        "output_dir",
        "prompt_template",
        "review_prompt_template",
        "generation_spec",
        "examples",
        "schema_file",
    )
    missing = [name for name in required if not isinstance(data.get(name), str)]
    if not isinstance(input_value, str):
        missing.append("input_file")
    if missing:
        raise ConfigurationError(f"missing string configuration keys: {', '.join(missing)}")
    assert isinstance(input_value, str)
    batch_size = batch_size_override or int(data.get("batch_size", 200))
    if batch_size < 1:
        raise ConfigurationError("batch_size must be positive")
    start_index = int(data.get("start_index", 1))
    if start_index < 1:
        raise ConfigurationError("start_index must be positive")
    expected_fields = int(data.get("expected_fields", 30))
    if expected_fields != 30:
        raise ConfigurationError("this schema profile requires exactly 30 fields")
    provider = provider_override or str(data.get("provider", "mock"))
    options = _mapping(data.get("provider_options", {}), "provider_options")
    repository_root = _resolve(base, str(data.get("repository_root", ".")))
    workspace = (
        workspace_override.resolve()
        if workspace_override
        else _resolve(base, str(data["workspace"]))
    )
    return ProjectConfig(
        config_path=resolved_config,
        project_root=repository_root,
        project_name=str(data.get("project_name", "lexicon_project")),
        words_file=_resolve(base, input_value),
        workspace=workspace,
        output_dir=_resolve(base, str(data["output_dir"])),
        prompt_template=_resolve(base, str(data["prompt_template"])),
        review_prompt_template=_resolve(base, str(data["review_prompt_template"])),
        generation_spec=_resolve(base, str(data["generation_spec"])),
        examples_file=_resolve(base, str(data["examples"])),
        schema_file=_resolve(base, str(data["schema_file"])),
        batch_size=batch_size,
        start_index=start_index,
        final_filename=str(data.get("final_filename", "lexicon.ai-reviewed.jsonl")),
        provider=provider,
        provider_options=options,
        expected_fields=expected_fields,
    )


def ensure_workspace_is_safe(config: ProjectConfig) -> None:
    workspace = config.workspace.resolve()
    root = config.project_root.resolve()
    output = config.output_dir.resolve()
    if workspace == root or root not in workspace.parents:
        raise ConfigurationError(
            f"workspace must be a descendant of the configuration directory: {workspace}"
        )
    if output == root or root not in output.parents:
        raise ConfigurationError(
            f"output_dir must be a descendant of the configuration directory: {output}"
        )
    if workspace == output or workspace in output.parents or output in workspace.parents:
        raise ConfigurationError("workspace and output_dir must be separate directories")
    if config.words_file == workspace or config.words_file == output:
        raise ConfigurationError("input file may not be overwritten by workspace or output")
    configured_files = (
        config.config_path,
        config.words_file,
        config.prompt_template,
        config.review_prompt_template,
        config.generation_spec,
        config.examples_file,
        config.schema_file,
    )
    escaped = [
        path
        for path in configured_files
        if path != root and root not in path.resolve().parents
    ]
    if escaped:
        raise ConfigurationError(f"configured paths escape repository root: {escaped}")
