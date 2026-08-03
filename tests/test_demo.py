from __future__ import annotations

from pathlib import Path

from lexicon_pipeline.audit import audit_public_release
from lexicon_pipeline.cli import main
from lexicon_pipeline.config import ProjectConfig


def test_cli_demo_is_offline_and_complete(temp_config: ProjectConfig) -> None:
    result = main(
        ["--config", str(temp_config.config_path), "demo", "--reset"]
    )
    assert result == 0
    assert (
        temp_config.output_dir / temp_config.final_filename
    ).read_text(encoding="utf-8").count("\n") == 15
    expected = temp_config.project_root / temp_config.provider_options["review_fixture"]
    assert (
        temp_config.output_dir / temp_config.final_filename
    ).read_bytes() == expected.read_bytes()


def test_public_release_audit_passes(repository_root: Path) -> None:
    result = audit_public_release(repository_root)
    assert result.passed, result.findings


def test_cli_accepts_config_after_subcommand(
    temp_config: ProjectConfig,
) -> None:
    assert main(["audit", "--config", str(temp_config.config_path)]) == 0
