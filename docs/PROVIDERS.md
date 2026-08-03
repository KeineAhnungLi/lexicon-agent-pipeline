# Providers

## MockProvider

Deterministic and offline. It copies two separate, clearly labeled synthetic fixtures. Use it for
tests, CI, Docker, and understanding artifact flow. It does not estimate model quality.

## CodexCLIProvider

Runs the locally installed Codex CLI once for generation and again for review. The container and
repository contain no authentication material. The host user must install, authenticate, and
inspect the CLI version independently.

Configurable options are executable name, timeout, optional model, and explicit extra arguments.
The repository does not enable approval or sandbox bypasses by default. Raw stdout/stderr are kept
inside the ignored local workspace for diagnosis and must not be published without review.

## Extension points

Implement `AgentProvider.run`, return `AgentRunResult`, preserve isolated generation/review calls,
write a complete output artifact, and expose actual model/provider provenance. Placeholder provider
names fail loudly until an implementation exists.
