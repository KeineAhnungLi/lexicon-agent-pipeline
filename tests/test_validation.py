from __future__ import annotations

import json
from pathlib import Path

from lexicon_pipeline.constants import AGENT_FIELD_NAMES
from lexicon_pipeline.validation import (
    normalize_expected_pos,
    validate_jsonl,
    with_derived_meaning_merged,
)


def test_public_fixture_has_15_valid_ordered_rows(repository_root: Path) -> None:
    path = repository_root / "examples" / "public_examples.jsonl"
    words = (repository_root / "examples" / "words.demo.tsv").read_text(
        encoding="utf-8"
    ).splitlines()[1:]
    report = validate_jsonl(path, expected_words=words, expected_first=1)
    assert report.valid
    assert report.row_count == 15


def test_invalid_json_is_reported(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text("{broken\n", encoding="utf-8")
    report = validate_jsonl(path)
    assert not report.valid
    assert report.issues[0].code == "INVALID_JSON"


def test_field_order_is_enforced(tmp_path: Path, repository_root: Path) -> None:
    source = repository_root / "examples" / "public_examples.jsonl"
    row = json.loads(source.read_text(encoding="utf-8").splitlines()[0])
    reversed_row = {key: row[key] for key in reversed(AGENT_FIELD_NAMES)}
    path = tmp_path / "reversed.jsonl"
    path.write_text(json.dumps(reversed_row, ensure_ascii=False) + "\n", encoding="utf-8")
    assert any(issue.code == "FIELD_ORDER" for issue in validate_jsonl(path).issues)


def test_word_identity_is_enforced(repository_root: Path) -> None:
    path = repository_root / "examples" / "public_examples.jsonl"
    report = validate_jsonl(path, expected_words=["different"] * 15, expected_first=1)
    assert any(issue.code == "WORD_MISMATCH" for issue in report.issues)


def test_expected_pos_alias_is_enforced(tmp_path: Path, repository_root: Path) -> None:
    source = repository_root / "examples" / "public_examples.jsonl"
    row = json.loads(source.read_text(encoding="utf-8").splitlines()[0])
    path = tmp_path / "pos.jsonl"
    path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    matching = validate_jsonl(
        path,
        expected_words=[str(row["word"])],
        expected_first=int(row["first"]),
        expected_pos=[str(row["class"])],
    )
    assert matching.valid
    mismatch_hint = "verb" if "V." not in str(row["class"]).split("/") else "noun"
    mismatch = validate_jsonl(
        path,
        expected_words=[str(row["word"])],
        expected_first=int(row["first"]),
        expected_pos=[mismatch_hint],
    )
    assert any(issue.code == "EXPECTED_POS_MISMATCH" for issue in mismatch.issues)


def test_production_source_pos_aliases_are_supported() -> None:
    assert normalize_expected_pos("contraction") == "Kontr."
    assert normalize_expected_pos("num") == "Num."
    assert normalize_expected_pos("postp") == "Postp."


def test_global_sequence_is_enforced(repository_root: Path) -> None:
    path = repository_root / "examples" / "public_examples.jsonl"
    report = validate_jsonl(path, expected_first=2)
    assert any(issue.code == "FIRST_SEQUENCE" for issue in report.issues)


def test_row_count_is_enforced(repository_root: Path) -> None:
    path = repository_root / "examples" / "public_examples.jsonl"
    report = validate_jsonl(path, expected_words=["Morgenlicht"], expected_first=1)
    assert any(issue.code == "ROW_COUNT" for issue in report.issues)


def test_extra_field_is_rejected(tmp_path: Path, repository_root: Path) -> None:
    row = json.loads(
        (repository_root / "examples" / "public_examples.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()[0]
    )
    row["extra"] = "not allowed"
    path = tmp_path / "extra.jsonl"
    path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    assert any(issue.code == "FIELD_ORDER" for issue in validate_jsonl(path).issues)


def test_final_meaning_merged_is_derived_and_tamper_evident(
    tmp_path: Path, repository_root: Path
) -> None:
    row = json.loads(
        (repository_root / "examples" / "public_examples.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()[0]
    )
    final = with_derived_meaning_merged(row)
    path = tmp_path / "final.jsonl"
    path.write_text(json.dumps(final, ensure_ascii=False) + "\n", encoding="utf-8")
    assert validate_jsonl(path, schema="final").valid
    final["meaning_merged"] = "tampered"
    path.write_text(json.dumps(final, ensure_ascii=False) + "\n", encoding="utf-8")
    report = validate_jsonl(path, schema="final")
    assert any(issue.code == "MEANING_MERGED_DERIVATION" for issue in report.issues)
