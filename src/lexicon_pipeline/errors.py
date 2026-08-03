from __future__ import annotations


class PipelineError(RuntimeError):
    """Base class for expected, user-actionable pipeline failures."""


class ConfigurationError(PipelineError):
    """Configuration is missing, inconsistent, or unsafe."""


class ProviderError(PipelineError):
    """An agent provider failed to produce an output."""


class ValidationFailure(PipelineError):
    """Mechanical validation failed."""


class StateError(PipelineError):
    """Workspace state is incomplete or internally inconsistent."""
