from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from lexicon_pipeline.errors import ConfigurationError, ProviderError
from lexicon_pipeline.providers.codex_cli import CodexCLIProvider, parse_tokens_used


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
        return subprocess.CompletedProcess(
            command, 0, stdout="done", stderr="tokens used\r\n170,585\r\n"
        )

    monkeypatch.setattr("lexicon_pipeline.providers.codex_cli.subprocess.run", fake_run)

    provider = CodexCLIProvider(
        tmp_path,
        {
            "model": "gpt-5.6-sol",
            "reasoning_effort": "xhigh",
            "extra_args": ["--ephemeral"],
        },
    )
    result = provider.run(
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
    assert '"tokens_used": 170585' in transcript
    assert result.reasoning_effort == "xhigh"
    assert result.tokens_used == 170585


def test_codex_provider_rejects_unknown_reasoning_effort(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="reasoning_effort"):
        CodexCLIProvider(tmp_path, {"reasoning_effort": "ultra"})


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("tokens used\n1,234", 1234),
        ("TOKENS USED 42", 42),
        ("tokens used\n10\ntokens used\n20", 20),
        ("no token footer", None),
    ],
)
def test_parse_tokens_used(text: str, expected: int | None) -> None:
    assert parse_tokens_used(text) == expected


def test_timeout_writes_partial_transcript_and_exact_tokens(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    transcript_path = tmp_path / "timeout.transcript.json"
    monkeypatch.setattr(
        "lexicon_pipeline.providers.codex_cli.shutil.which",
        lambda executable: "/usr/bin/codex",
    )

    def time_out(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        raise subprocess.TimeoutExpired(
            command,
            timeout=30,
            output=b"partial response",
            stderr=b"tokens used\r\n9,876\r\n",
        )

    monkeypatch.setattr("lexicon_pipeline.providers.codex_cli.subprocess.run", time_out)
    provider = CodexCLIProvider(
        tmp_path,
        {"timeout_seconds": 30, "model": "gpt-5.6-sol", "reasoning_effort": "xhigh"},
    )

    with pytest.raises(ProviderError, match="partial transcript"):
        provider.run(
            stage="generation",
            prompt="Generate.",
            output_path=tmp_path / "generated.jsonl",
            transcript_path=transcript_path,
        )

    transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
    assert transcript["timed_out"] is True
    assert transcript["returncode"] is None
    assert transcript["reasoning_effort"] == "xhigh"
    assert transcript["tokens_used"] == 9876
