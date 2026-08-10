from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from lexicon_pipeline.errors import ConfigurationError
from lexicon_pipeline.providers.codex_cli import CodexCLIProvider


def test_codex_provider_passes_model_and_reasoning_effort(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    output_path = tmp_path / "batch.generated.jsonl"
    transcript_path = tmp_path / "generation.transcript.json"
    captured: dict[str, list[str]] = {}

    monkeypatch.setattr(
        "lexicon_pipeline.providers.codex_cli.shutil.which",
        lambda executable: "/usr/bin/codex",
    )

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        output_path.write_text("{}\n", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr("lexicon_pipeline.providers.codex_cli.subprocess.run", fake_run)

    provider = CodexCLIProvider(
        tmp_path,
        {
            "model": "gpt-5.6-sol",
            "reasoning_effort": "xhigh",
            "extra_args": ["--ephemeral"],
        },
    )
    provider.run(
        stage="generation",
        prompt="Generate the batch.",
        output_path=output_path,
        transcript_path=transcript_path,
    )

    command = captured["command"]
    assert command[:4] == ["/usr/bin/codex", "exec", "-C", str(tmp_path)]
    assert ["--model", "gpt-5.6-sol"] == command[4:6]
    assert ["--config", 'model_reasoning_effort="xhigh"'] == command[6:8]
    assert command[-2:] == ["--ephemeral", "-"]
    transcript = transcript_path.read_text(encoding="utf-8")
    assert '"model": "gpt-5.6-sol"' in transcript
    assert '"reasoning_effort": "xhigh"' in transcript


def test_codex_provider_rejects_unknown_reasoning_effort(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="reasoning_effort"):
        CodexCLIProvider(tmp_path, {"reasoning_effort": "ultra"})
