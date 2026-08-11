from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from lexicon_pipeline.constants import (
    AGENT_FIELD_NAMES,
    ALLOWED_CLASS_OPTIONS,
    ALLOWED_CLASS_PARTS,
    EXPECTED_POS_ALIASES,
    FINAL_FIELD_NAMES,
    MISSING_VALUE,
)

ArtifactSchema = Literal["agent", "final"]


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
    schema: ArtifactSchema
    issues: tuple[ValidationIssue, ...]

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["issues"] = [asdict(issue) for issue in self.issues]
        return result


def normalize_expected_pos(value: str) -> str | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    if cleaned in ALLOWED_CLASS_PARTS:
        return cleaned
    return EXPECTED_POS_ALIASES.get(cleaned.casefold())


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[ValidationIssue]]:
    rows: list[dict[str, Any]] = []
    issues: list[ValidationIssue] = []
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
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


def expected_class_option(word_class: str) -> str | None:
    parts = word_class.split("/")
    if any(part not in ALLOWED_CLASS_PARTS for part in parts):
        return None
    if "N." in parts or "Abk." in parts:
        return "N."
    if "V." in parts:
        return "V."
    if "Adj." in parts:
        return "Adj."
    if word_class == "Wend.":
        return "Wend."
    return "others"


def derive_meaning_merged(row: dict[str, Any]) -> str:
    return "；".join(
        str(row[f"meaning{number}"])
        for number in range(1, 8)
        if row.get(f"meaning{number}") != MISSING_VALUE
    )


def with_derived_meaning_merged(row: dict[str, Any]) -> dict[str, Any]:
    return {
        field: derive_meaning_merged(row) if field == "meaning_merged" else row[field]
        for field in FINAL_FIELD_NAMES
    }


def validate_jsonl(
    path: Path,
    *,
    expected_words: list[str] | None = None,
    expected_first: int | None = None,
    expected_pos: list[str] | None = None,
    schema: ArtifactSchema = "agent",
) -> ValidationReport:
    rows, issues = read_jsonl(path)
    expected_count = len(expected_words) if expected_words is not None else None
    field_names = AGENT_FIELD_NAMES if schema == "agent" else FINAL_FIELD_NAMES
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
            ValidationIssue("ROW_COUNT", f"expected {expected_count} records, found {len(rows)}")
        )
    for offset, row in enumerate(rows):
        line = offset + 1
        if tuple(row) != field_names:
            issues.append(
                ValidationIssue(
                    "FIELD_ORDER",
                    f"expected {schema} fields in canonical order; found {list(row)}",
                    line,
                )
            )
            continue
        for name, value in row.items():
            if not isinstance(value, (str, int)):
                issues.append(
                    ValidationIssue(
                        "FIELD_TYPE", "field must be a string or integer", line, name
                    )
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
        if (
            expected_words is not None
            and offset < len(expected_words)
            and row["word"] != expected_words[offset]
        ):
            issues.append(
                ValidationIssue(
                    "WORD_MISMATCH",
                    f"expected {expected_words[offset]!r}, found {row['word']!r}",
                    line,
                    "word",
                )
            )
        word_class = str(row["class"])
        option = expected_class_option(word_class)
        if option is None:
            issues.append(
                ValidationIssue(
                    "CLASS_VALUE", f"unsupported class {word_class!r}", line, "class"
                )
            )
        if row["class_options"] not in ALLOWED_CLASS_OPTIONS:
            issues.append(
                ValidationIssue(
                    "CLASS_OPTION_VALUE",
                    f"unsupported class_options {row['class_options']!r}",
                    line,
                    "class_options",
                )
            )
        elif option is not None and row["class_options"] != option:
            issues.append(
                ValidationIssue(
                    "CLASS_OPTION_MISMATCH",
                    f"class {word_class!r} requires class_options {option!r}",
                    line,
                    "class_options",
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
                        "class",
                    )
                )
            elif normalized not in word_class.split("/"):
                issues.append(
                    ValidationIssue(
                        "EXPECTED_POS_MISMATCH",
                        f"expected class component {normalized!r} from hint "
                        f"{expected_pos[offset]!r}, found {word_class!r}",
                        line,
                        "class",
                    )
                )
        if not str(row["correct_option"]).startswith(f"{word_class} "):
            issues.append(
                ValidationIssue(
                    "CORRECT_OPTION_PREFIX",
                    "correct_option must start with the exact class and one space",
                    line,
                    "correct_option",
                )
            )
        if row["meaning1"] == MISSING_VALUE:
            issues.append(
                ValidationIssue(
                    "REQUIRED_MEANING", "meaning1 may not be missing", line, "meaning1"
                )
            )
        for number in range(1, 8):
            collocation = row[f"collocation{number}"]
            translation = row[f"collocation{number}_translation"]
            if (collocation == MISSING_VALUE) != (translation == MISSING_VALUE):
                issues.append(
                    ValidationIssue(
                        "COLLOCATION_PAIR",
                        f"collocation{number} and its translation must both be present "
                        "or both be —",
                        line,
                    )
                )
            if str(row[f"meaning{number}"]).startswith("v."):
                issues.append(
                    ValidationIssue(
                        "LOWERCASE_VERB_LABEL",
                        "verb meaning labels must use Vt./Vi./Vr./Vimp., not v.",
                        line,
                        f"meaning{number}",
                    )
                )
        if schema == "final" and row["meaning_merged"] != derive_meaning_merged(row):
            issues.append(
                ValidationIssue(
                    "MEANING_MERGED_DERIVATION",
                    "meaning_merged must equal the mechanical join of non-dash meaning1..meaning7",
                    line,
                    "meaning_merged",
                )
            )
    return ValidationReport(
        path=str(path),
        valid=not issues,
        row_count=len(rows),
        expected_row_count=expected_count,
        schema=schema,
        issues=tuple(issues),
    )
