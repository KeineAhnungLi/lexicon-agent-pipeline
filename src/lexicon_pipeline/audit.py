from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

from lexicon_pipeline.io_utils import atomic_write_json, atomic_write_text
from lexicon_pipeline.validation import validate_jsonl


@dataclass(frozen=True)
class AuditFinding:
    severity: str
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class AuditResult:
    passed: bool
    findings: tuple[AuditFinding, ...]


TEXT_SUFFIXES = frozenset(
    {".md", ".txt", ".json", ".jsonl", ".py", ".toml", ".yml", ".yaml", ".ini", ".cfg"}
)
IGNORED_PARTS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "site",
        "demo_workspace",
        "reports",
        ".audit-reports",
        "runtime",
    }
)
MAX_PUBLIC_FILE_BYTES = 2 * 1024 * 1024
MAX_PUBLIC_REPOSITORY_BYTES = 10 * 1024 * 1024
REQUIRED_FILES = (
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "AGENTS.md",
    "NEXT_AGENT_PROMPT.md",
    "PUBLIC_DATA_POLICY.md",
    "PRIVATE_DATA.md",
    "LICENSE",
    "DATA_LICENSE",
    "project.example.json",
    "schemas/lexicon_record.schema.json",
    "examples/words.demo.tsv",
    "tests/test_demo.py",
    ".github/workflows/ci.yml",
)


def _files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file() and not any(part in IGNORED_PARTS for part in path.parts):
            yield path


def audit_public_release(root: Path) -> AuditResult:
    root = root.resolve()
    findings: list[AuditFinding] = []
    for required in REQUIRED_FILES:
        if not (root / required).is_file():
            findings.append(
                AuditFinding("error", "MISSING_REQUIRED", required, "required file absent")
            )
    path_pattern = re.compile(
        r"(?:[A-Za-z]:[\\/](?:Users|Documents and Settings)[\\/]|/(?:home|Users)/[^/\s]+/)"
    )
    email_pattern = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
    phone_pattern = re.compile(r"(?<!\d)(?:\+\d{1,3}[- ]?)?\d{3}[- ]\d{3}[- ]\d{4}(?!\d)")
    cookie_pattern = re.compile(r"\b(?:cookie|set-cookie)\s*[:=]", re.IGNORECASE)
    secret_fragments = (
        ("sk" + "-", re.compile(r"\bsk-[A-Za-z0-9_-]{16,}")),
        ("private-key", re.compile("BEGIN " + "PRIVATE KEY")),
        ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}")),
    )
    forbidden_names = {
        "project.json",
        ".env",
        "examples.jsonl",
        "source.xlsx",
        "full_output.jsonl",
    }
    forbidden_suffixes = {".xlsx", ".xls", ".zip", ".7z"}
    total_size = 0
    for path in _files(root):
        relative = path.relative_to(root).as_posix()
        size = path.stat().st_size
        total_size += size
        if size > MAX_PUBLIC_FILE_BYTES:
            findings.append(
                AuditFinding("error", "LARGE_FILE", relative, f"{size} bytes exceeds public limit")
            )
        if path.name in forbidden_names:
            findings.append(
                AuditFinding("error", "PRIVATE_FILENAME", relative, "private/local artifact name")
            )
        if (
            relative.startswith(("workspace/", "workspaces/", "outputs/"))
            and path.name != ".gitkeep"
        ):
            findings.append(
                AuditFinding(
                    "error",
                    "RUNTIME_ARTIFACT",
                    relative,
                    "workspace/output artifacts may not enter a public release",
                )
            )
        if path.suffix.lower() in forbidden_suffixes:
            findings.append(
                AuditFinding("error", "PRIVATE_ARCHIVE_OR_SHEET", relative, "archive/sheet found")
            )
        if "transcript" in path.name.lower() and "fixtures" not in path.parts:
            findings.append(
                AuditFinding(
                    "error",
                    "TRANSCRIPT_FILE",
                    relative,
                    "transcript requires manual review",
                )
            )
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(
                AuditFinding("error", "NON_UTF8", relative, "public text files must be UTF-8")
            )
            continue
        if relative != "src/lexicon_pipeline/audit.py" and path_pattern.search(text):
            findings.append(
                AuditFinding("error", "ABSOLUTE_USER_PATH", relative, "machine-specific path found")
            )
        if relative != "src/lexicon_pipeline/audit.py":
            for label, pattern in secret_fragments:
                if pattern.search(text):
                    findings.append(
                        AuditFinding("error", "POSSIBLE_SECRET", relative, f"{label} pattern found")
                    )
            for code, pattern in (
                ("POSSIBLE_EMAIL", email_pattern),
                ("POSSIBLE_PHONE", phone_pattern),
                ("POSSIBLE_COOKIE", cookie_pattern),
            ):
                if pattern.search(text):
                    findings.append(
                        AuditFinding("error", code, relative, "possible personal/auth data found")
                    )
    if total_size > MAX_PUBLIC_REPOSITORY_BYTES:
        findings.append(
            AuditFinding(
                "error",
                "REPOSITORY_SIZE",
                ".",
                f"{total_size} bytes exceeds the public source-tree limit",
            )
        )
    examples = root / "examples" / "public_examples.jsonl"
    words_file = root / "examples" / "words.demo.tsv"
    if examples.is_file() and words_file.is_file():
        words = words_file.read_text(encoding="utf-8-sig").splitlines()
        demo_words = words[1:] if words and words[0] == "word" else []
        report = validate_jsonl(examples, expected_words=demo_words, expected_first=1)
        if not report.valid or not 15 <= report.row_count <= 30:
            findings.append(
                AuditFinding(
                    "error",
                    "PUBLIC_EXAMPLES",
                    examples.relative_to(root).as_posix(),
                    "public examples must be 15–30 valid records aligned to demo input",
                )
            )
    prompt = root / "prompts" / "prompt_template.md"
    if prompt.is_file():
        prompt_text = prompt.read_text(encoding="utf-8")
        required_markers = (
            "{{WORD_LIST}}",
            "{{GENERATION_SPEC}}",
            "{{EXAMPLES}}",
            "{{START_INDEX}}",
        )
        if any(marker not in prompt_text for marker in required_markers):
            findings.append(
                AuditFinding("error", "PROMPT_PLACEHOLDERS", str(prompt), "required marker absent")
            )
    readme = root / "README.md"
    if readme.is_file():
        readme_text = readme.read_text(encoding="utf-8").lower()
        for phrase in ("4,812", "mockprovider", "does not", "independent"):
            if phrase.lower() not in readme_text:
                findings.append(
                    AuditFinding("error", "README_BOUNDARY", "README.md", f"missing {phrase!r}")
                )
    return AuditResult(
        passed=not any(item.severity == "error" for item in findings),
        findings=tuple(findings),
    )


def write_audit_report(root: Path, result: AuditResult, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "public_release_audit.json"
    md_path = output_dir / "public_release_audit.md"
    atomic_write_json(
        json_path,
        {
            "root": root.name,
            "passed": result.passed,
            "findings": [asdict(item) for item in result.findings],
            "license_selected": True,
            "code_license": "MIT",
            "data_license": "CC0-1.0",
        },
    )
    lines = [
        "# Public release audit",
        "",
        f"Operational audit: **{'PASS' if result.passed else 'FAIL'}**",
        "",
        "Licenses: **MIT** for code/prompts/docs and **CC0-1.0** for public synthetic data.",
        "",
    ]
    if result.findings:
        lines.extend(["| Severity | Code | Path | Message |", "|---|---|---|---|"])
        lines.extend(
            f"| {item.severity} | {item.code} | `{item.path}` | {item.message} |"
            for item in result.findings
        )
    else:
        lines.append("No blocking content, path, secret, size, or required-file findings.")
    atomic_write_text(md_path, "\n".join(lines) + "\n")
    return json_path, md_path
