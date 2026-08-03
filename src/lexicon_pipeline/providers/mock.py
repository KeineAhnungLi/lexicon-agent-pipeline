from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from lexicon_pipeline.errors import ConfigurationError
from lexicon_pipeline.io_utils import atomic_write_json, atomic_write_text
from lexicon_pipeline.providers.base import AgentRunResult


class MockProvider:
    """Deterministic fixture provider for tests and the public no-cost demo."""

    def __init__(self, base: Path, options: Mapping[str, Any]) -> None:
        self.base = base
        self.options = options

    def _fixture(self, stage: str) -> Path:
        key = "generation_fixture" if stage == "generation" else "review_fixture"
        value = self.options.get(key)
        if not isinstance(value, str):
            raise ConfigurationError(f"mock provider requires provider_options.{key}")
        return (self.base / value).resolve()

    def run(
        self,
        *,
        stage: str,
        prompt: str,
        output_path: Path,
        transcript_path: Path,
    ) -> AgentRunResult:
        del prompt
        fixture = self._fixture(stage)
        atomic_write_text(output_path, fixture.read_text(encoding="utf-8"))
        atomic_write_json(
            transcript_path,
            {
                "provider": "mock",
                "stage": stage,
                "fixture": fixture.name,
                "notice": "Synthetic fixture replay; no model was called.",
            },
        )
        return AgentRunResult(
            provider="mock",
            stage=stage,
            output_path=output_path,
            transcript_path=transcript_path,
            command=("mock-fixture-copy",),
            model=None,
        )
