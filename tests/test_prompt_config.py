from __future__ import annotations

import json
from pathlib import Path

import pytest

from lexicon_pipeline.config import ConfigurationError, ProjectConfig, ensure_workspace_is_safe
from lexicon_pipeline.errors import StateError
from lexicon_pipeline.io_utils import atomic_write_text, sha256_file
from lexicon_pipeline.manifest import new_manifest
from lexicon_pipeline.prepare import read_input_entries, read_words
from lexicon_pipeline.rendering import render_text


def test_render_substitutes_batch_values(temp_config: ProjectConfig) -> None:
    manifest = new_manifest(temp_config, ["Alpha", "Beta"])
    rendered = render_text(
        "{{BATCH_ID}} {{START_INDEX}} {{END_INDEX}}\n{{WORD_LIST}}\n"
        "{{GENERATION_SPEC}}\n{{EXAMPLES}}",
        manifest["batches"][0],
        generation_spec="spec",
        examples="examples",
    )
    assert "batch_01 1 2" in rendered
    assert "1. Alpha" in rendered
    assert "{{" not in rendered


def test_duplicate_words_without_pos_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "words.txt"
    path.write_text("word\neins\neins\n", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="duplicate"):
        read_words(path)


def test_homographs_with_distinct_expected_pos_are_allowed(tmp_path: Path) -> None:
    path = tmp_path / "words.tsv"
    path.write_text(
        "word\texpected_pos\nüberlegen\tadj\nüberlegen\tverb\n",
        encoding="utf-8",
    )
    words, positions = read_input_entries(path)
    assert words == ["überlegen", "überlegen"]
    assert positions == ["adj", "verb"]


def test_duplicate_words_with_same_expected_pos_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "words.tsv"
    path.write_text(
        "word\texpected_pos\nüberlegen\tverb\nüberlegen\tverb\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigurationError, match="unique non-empty expected_pos"):
        read_words(path)


def test_render_includes_expected_pos_without_changing_word(temp_config: ProjectConfig) -> None:
    manifest = new_manifest(
        temp_config,
        ["überlegen", "überlegen"],
        expected_pos=["adj", "verb"],
    )
    rendered = render_text(
        "{{WORD_LIST}}",
        manifest["batches"][0],
    )
    assert "1. überlegen\t[expected_pos=adj]" in rendered
    assert "2. überlegen\t[expected_pos=verb]" in rendered


def test_missing_word_header_rejected(tmp_path: Path) -> None:
    path = tmp_path / "words.tsv"
    path.write_text("Abend\n", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="word header"):
        read_words(path)


def test_empty_input_rejected(tmp_path: Path) -> None:
    path = tmp_path / "words.tsv"
    path.write_text("word\n", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="no non-empty"):
        read_words(path)


def test_utf8_bom_is_supported(tmp_path: Path) -> None:
    path = tmp_path / "words.tsv"
    path.write_text("word\nÄhre\n", encoding="utf-8-sig")
    assert read_words(path) == ["Ähre"]


def test_missing_prompt_placeholder_is_rejected(temp_config: ProjectConfig) -> None:
    manifest = new_manifest(temp_config, ["Alpha"])
    with pytest.raises(StateError, match="missing required placeholders"):
        render_text(
            "{{WORD_LIST}} {{START_INDEX}}",
            manifest["batches"][0],
            require_content_placeholders=True,
        )


def test_workspace_must_be_descendant(temp_config: ProjectConfig) -> None:
    unsafe = ProjectConfig(
        **{**temp_config.__dict__, "workspace": temp_config.project_root}
    )
    with pytest.raises(ConfigurationError, match="descendant"):
        ensure_workspace_is_safe(unsafe)


def test_schema_is_valid_json(repository_root: Path) -> None:
    schema = json.loads(
        (repository_root / "schemas" / "lexicon_record.schema.json").read_text(encoding="utf-8")
    )
    assert len(schema["required"]) == 30
    assert schema["additionalProperties"] is False


def test_batching_respects_start_index(temp_config: ProjectConfig) -> None:
    shifted = ProjectConfig(**{**temp_config.__dict__, "batch_size": 2, "start_index": 7})
    manifest = new_manifest(shifted, ["a", "b", "c"])
    assert [(item["start"], item["end"]) for item in manifest["batches"]] == [(7, 8), (9, 9)]


def test_atomic_write_replaces_complete_file(tmp_path: Path) -> None:
    path = tmp_path / "artifact.txt"
    atomic_write_text(path, "first\n")
    first_hash = sha256_file(path)
    atomic_write_text(path, "second\n")
    assert path.read_text(encoding="utf-8") == "second\n"
    assert sha256_file(path) != first_hash
