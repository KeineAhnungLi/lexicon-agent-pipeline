from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from lexicon_pipeline.constants import (
    ALLOWED_LEVELS,
    ALLOWED_POS,
    ALLOWED_REGIONS,
    ALLOWED_REGISTER,
    FIELD_NAMES,
    MISSING_VALUE,
)

EXPECTED_POS_ALIASES = {
    "adj": "Adjektiv",
    "adjective": "Adjektiv",
    "adjektiv": "Adjektiv",
    "adv": "Adverb",
    "adverb": "Adverb",
    "art": "Artikel",
    "article": "Artikel",
    "artikel": "Artikel",
    "intj": "Interjektion",
    "interjection": "Interjektion",
    "interjektion": "Interjektion",
    "conj": "Konjunktion",
    "conjunction": "Konjunktion",
    "konjunktion": "Konjunktion",
    "n": "Nomen",
    "noun": "Nomen",
    "nomen": "Nomen",
    "substantiv": "Nomen",
    "part": "Partikel",
    "particle": "Partikel",
    "partikel": "Partikel",
    "phr": "Phrase",
    "phrase": "Phrase",
    "prep": "Präposition",
    "preposition": "Präposition",
    "präposition": "Präposition",
    "praeposition": "Präposition",
    "pron": "Pronomen",
    "pronoun": "Pronomen",
    "pronomen": "Pronomen",
    "v": "Verb",
    "verb": "Verb",
}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    line: int | None = None
    field: str | None = None


@dataclass(frozen=True)
class ValidationReport:
    path: str
    valid: bool
    row_count: int
    expected_row_count: int | None
    issues: tuple[ValidationIssue, ...]

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["issues"] = [asdict(issue) for issue in self.issues]
        return result


def normalize_expected_pos(value: str) -> str | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    if cleaned in ALLOWED_POS:
        return cleaned
    return EXPECTED_POS_ALIASES.get(cleaned.casefold())


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[ValidationIssue]]:
    rows: list[dict[str, Any]] = []
    issues: list[ValidationIssue] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [], [ValidationIssue("FILE_READ", str(exc))]
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            issues.append(ValidationIssue("BLANK_LINE", "blank lines are not allowed", number))
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            issues.append(ValidationIssue("INVALID_JSON", str(exc), number))
            continue
        if not isinstance(value, dict):
            issues.append(ValidationIssue("NOT_OBJECT", "record must be a JSON object", number))
            continue
        rows.append(value)
    return rows, issues


def validate_jsonl(
    path: Path,
    *,
    expected_words: list[str] | None = None,
    expected_first: int | None = None,
    expected_pos: list[str] | None = None,
) -> ValidationReport:
    rows, issues = read_jsonl(path)
    expected_count = len(expected_words) if expected_words is not None else None
    if (
        expected_pos is not None
        and expected_words is not None
        and len(expected_pos) != len(expected_words)
    ):
        issues.append(
            ValidationIssue(
                "EXPECTED_POS_ALIGNMENT",
                "expected_pos hints must align one-to-one with expected_words",
            )
        )
    if expected_count is not None and len(rows) != expected_count:
        issues.append(
            ValidationIssue(
                "ROW_COUNT",
                f"expected {expected_count} records, found {len(rows)}",
            )
        )
    for offset, row in enumerate(rows):
        line = offset + 1
        keys = tuple(row.keys())
        if keys != FIELD_NAMES:
            issues.append(
                ValidationIssue(
                    "FIELD_ORDER",
                    f"expected fields in canonical order; found {list(keys)}",
                    line,
                )
            )
            continue
        for name, value in row.items():
            if not isinstance(value, (str, int)):
                issues.append(
                    ValidationIssue("FIELD_TYPE", "field must be a string or integer", line, name)
                )
            elif isinstance(value, str) and not value.strip():
                issues.append(ValidationIssue("EMPTY_VALUE", "use — for missing data", line, name))
        if not isinstance(row["first"], int):
            issues.append(ValidationIssue("FIRST_TYPE", "first must be an integer", line, "first"))
        elif expected_first is not None and row["first"] != expected_first + offset:
            issues.append(
                ValidationIssue(
                    "FIRST_SEQUENCE",
                    f"expected {expected_first + offset}, found {row['first']}",
                    line,
                    "first",
                )
            )
        if expected_words is not None and offset < len(expected_words):
            if row["word"] != expected_words[offset]:
                issues.append(
                    ValidationIssue(
                        "WORD_MISMATCH",
                        f"expected {expected_words[offset]!r}, found {row['word']!r}",
                        line,
                        "word",
                    )
                )
        if expected_pos is not None and offset < len(expected_pos) and expected_pos[offset].strip():
            normalized = normalize_expected_pos(expected_pos[offset])
            if normalized is None:
                issues.append(
                    ValidationIssue(
                        "EXPECTED_POS_VALUE",
                        f"unsupported expected_pos hint {expected_pos[offset]!r}",
                        line,
                        "pos",
                    )
                )
            elif row["pos"] != normalized:
                issues.append(
                    ValidationIssue(
                        "EXPECTED_POS_MISMATCH",
                        f"expected pos {normalized!r} from hint {expected_pos[offset]!r}, "
                        f"found {row['pos']!r}",
                        line,
                        "pos",
                    )
                )
        for field, allowed in (
            ("level", ALLOWED_LEVELS),
            ("pos", ALLOWED_POS),
            ("register", ALLOWED_REGISTER),
            ("region", ALLOWED_REGIONS),
        ):
            if row[field] not in allowed:
                issues.append(
                    ValidationIssue(
                        "ENUM_VALUE",
                        f"{row[field]!r} is outside the mechanical allow-list",
                        line,
                        field,
                    )
                )
        if row["meaning"] == MISSING_VALUE:
            issues.append(
                ValidationIssue("REQUIRED_MEANING", "meaning may not be missing", line, "meaning")
            )
        if (row["example"] == MISSING_VALUE) != (row["translation"] == MISSING_VALUE):
            issues.append(
                ValidationIssue(
                    "EXAMPLE_PAIR",
                    "example and translation must both be present or both be —",
                    line,
                )
            )
    return ValidationReport(
        path=str(path),
        valid=not issues,
        row_count=len(rows),
        expected_row_count=expected_count,
        issues=tuple(issues),
    )
