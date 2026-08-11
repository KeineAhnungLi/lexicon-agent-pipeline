from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class AgentRunResult:
    provider: str
    stage: str
    output_path: Path
    transcript_path: Path | None
    command: tuple[str, ...]
    model: str | None = None
    reasoning_effort: str | None = None
    tokens_used: int | None = None


class AgentProvider(Protocol):
    def run(
        self,
        *,
        stage: str,
        prompt: str,
        output_path: Path,
        transcript_path: Path,
    ) -> AgentRunResult:
        """Run one isolated agent invocation and write its complete output."""
        ...
