from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from lexicon_pipeline.config import ProjectConfig, ensure_workspace_is_safe
from lexicon_pipeline.errors import ConfigurationError
from lexicon_pipeline.io_utils import atomic_write_text
from lexicon_pipeline.manifest import new_manifest, save_manifest


def read_input_entries(path: Path) -> tuple[list[str], list[str]]:
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        raise ConfigurationError(f"cannot read words file {path}: {exc}") from exc
    if not lines:
        raise ConfigurationError("input TSV must begin with a word header")
    headers = [cell.strip() for cell in lines[0].lstrip("\ufeff").split("\t")]
    if not headers or headers[0] != "word":
        raise ConfigurationError("input TSV must begin with a word header")
    expected_pos_index = headers.index("expected_pos") if "expected_pos" in headers else None
    words: list[str] = []
    expected_pos: list[str] = []
    for line in lines[1:]:
        if not line.strip():
            continue
        cells = line.split("\t")
        word = cells[0].strip()
        if not word:
            raise ConfigurationError("words file contains an empty word entry")
        pos = ""
        if expected_pos_index is not None and expected_pos_index < len(cells):
            pos = cells[expected_pos_index].strip()
        words.append(word)
        expected_pos.append(pos)
    if not words:
        raise ConfigurationError("words file has no non-empty entries")

    grouped: dict[str, list[str]] = {}
    for word, pos in zip(words, expected_pos, strict=True):
        grouped.setdefault(word, []).append(pos)
    for word, positions in grouped.items():
        if len(positions) < 2:
            continue
        if any(not pos for pos in positions) or len(set(positions)) != len(positions):
            raise ConfigurationError(
                "duplicate word entries require unique non-empty expected_pos values: "
                f"{word!r} -> {positions}"
            )
    return words, expected_pos


def read_words(path: Path) -> list[str]:
    words, _ = read_input_entries(path)
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
    words, expected_pos = read_input_entries(config.words_file)
    atomic_write_text(workspace / "input_words.txt", "\n".join(words) + "\n")
    manifest = new_manifest(config, words, expected_pos=expected_pos)
    save_manifest(config.manifest_path, manifest)
    return manifest
