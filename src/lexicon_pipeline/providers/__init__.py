from __future__ import annotations

from lexicon_pipeline.config import ProjectConfig
from lexicon_pipeline.errors import ConfigurationError
from lexicon_pipeline.providers.base import AgentProvider
from lexicon_pipeline.providers.codex_cli import CodexCLIProvider
from lexicon_pipeline.providers.mock import MockProvider


def create_provider(config: ProjectConfig) -> AgentProvider:
    if config.provider == "mock":
        return MockProvider(config.project_root, config.provider_options)
    if config.provider == "codex-cli":
        return CodexCLIProvider(config.project_root, config.provider_options)
    if config.provider in {"openai-api", "anthropic-api"}:
        raise ConfigurationError(
            f"provider {config.provider!r} is a documented extension point, not implemented"
        )
    raise ConfigurationError(f"unknown provider: {config.provider}")
