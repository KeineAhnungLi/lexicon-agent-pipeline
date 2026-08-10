from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from lexicon_pipeline.errors import ConfigurationError, ProviderError
from lexicon_pipeline.io_utils import atomic_write_text
from lexicon_pipeline.providers.base import AgentRunResult


REASONING_EFFORTS = frozenset({"none", "low", "medium", "high", "xhigh", "max"})


class CodexCLIProvider:
    """Adapter for a locally installed, already authenticated Codex CLI."""

    def __init__(self, working_directory: Path, options: Mapping[str, Any]) -> None:
        self.working_directory = working_directory
        self.executable = str(options.get("executable", "codex"))
        self.timeout = int(options.get("timeout_seconds", 1800))
        model = options.get("model")
        self.model = str(model) if model else None
        raw_effort = options.get("reasoning_effort")
        if raw_effort is None:
            self.reasoning_effort = None
        elif not isinstance(raw_effort, str) or raw_effort not in REASONING_EFFORTS:
            allowed = ", ".join(sorted(REASONING_EFFORTS))
            raise ConfigurationError(
                f"provider_options.reasoning_effort must be one of: {allowed}"
            )
        else:
            self.reasoning_effort = raw_effort
        raw_args = options.get("extra_args", [])
        if not isinstance(raw_args, list) or not all(isinstance(item, str) for item in raw_args):
            raise ConfigurationError("provider_options.extra_args must be a string array")
        self.extra_args = tuple(raw_args)

    def run(
        self,
        *,
        stage: str,
        prompt: str,
        output_path: Path,
        transcript_path: Path,
    ) -> AgentRunResult:
        executable = shutil.which(self.executable)
        if executable is None:
            raise ProviderError(
                f"Codex CLI executable {self.executable!r} was not found on PATH"
            )
        instruction = (
            f"{prompt}\n\nWrite the requested final JSONL artifact to {output_path}. "
            "Do not modify repository source files."
        )
        command = [executable, "exec", "-C", str(self.working_directory)]
        if self.model:
            command.extend(["--model", self.model])
        if self.reasoning_effort:
            command.extend(
                ["--config", f'model_reasoning_effort="{self.reasoning_effort}"']
            )
        command.extend(self.extra_args)
        command.append("-")
        try:
            completed = subprocess.run(
                command,
                input=instruction,
                text=True,
                encoding="utf-8",
                capture_output=True,
                timeout=self.timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ProviderError(f"Codex {stage} invocation failed: {exc}") from exc
        transcript = {
            "provider": "codex-cli",
            "stage": stage,
            "command": [Path(command[0]).name, *command[1:]],
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "model": self.model,
            "reasoning_effort": self.reasoning_effort,
        }
        atomic_write_text(
            transcript_path,
            json.dumps(transcript, ensure_ascii=False, indent=2) + "\n",
        )
        if completed.returncode != 0:
            raise ProviderError(
                f"Codex {stage} exited with {completed.returncode}; see {transcript_path}"
            )
        if not output_path.is_file():
            raise ProviderError(
                f"Codex {stage} returned successfully but did not create {output_path}"
            )
        return AgentRunResult(
            provider="codex-cli",
            stage=stage,
            output_path=output_path,
            transcript_path=transcript_path,
            command=tuple(command),
            model=self.model,
        )
