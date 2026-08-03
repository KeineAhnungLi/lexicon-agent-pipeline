from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from lexicon_pipeline.config import ProjectConfig, ensure_workspace_is_safe
from lexicon_pipeline.errors import ConfigurationError
from lexicon_pipeline.io_utils import atomic_write_text
from lexicon_pipeline.manifest import new_manifest, save_manifest


def read_words(path: Path) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        raise ConfigurationError(f"cannot read words file {path}: {exc}") from exc
    if not lines or lines[0].lstrip("\ufeff").strip().split("\t")[0] != "word":
        raise ConfigurationError("input TSV must begin with a word header")
    words = [line.split("\t", 1)[0].strip() for line in lines[1:] if line.strip()]
    if not words:
        raise ConfigurationError("words file has no non-empty entries")
    if len(words) != len(set(words)):
        raise ConfigurationError("words file contains duplicate entries")
    return words


def prepare_workspace(
    config: ProjectConfig,
    *,
    force_reset: bool = False,
    confirmed: bool = False,
) -> dict[str, Any]:
    ensure_workspace_is_safe(config)
    workspace = config.workspace
    if workspace.exists() and any(workspace.iterdir()):
        if not force_reset:
            raise ConfigurationError(
                f"workspace is not empty: {workspace}; use --force-reset to replace it"
            )
        if not confirmed:
            raise ConfigurationError("--force-reset also requires --yes")
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    for directory in (
        config.prompts_dir,
        config.outputs_dir,
        config.reports_dir,
        config.transcripts_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    config.output_dir.mkdir(parents=True, exist_ok=True)
    words = read_words(config.words_file)
    atomic_write_text(workspace / "input_words.txt", "\n".join(words) + "\n")
    manifest = new_manifest(config, words)
    save_manifest(config.manifest_path, manifest)
    return manifest
