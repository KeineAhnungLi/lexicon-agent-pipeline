# Providers

## MockProvider

Deterministic and offline. It copies two separate, clearly labeled synthetic fixtures. Use it for
tests, CI, Docker, and understanding artifact flow. It does not estimate model quality.

## CodexCLIProvider

Runs the locally installed Codex CLI once for generation and again for review. The container and
repository contain no authentication material. The host user must install, authenticate, and
inspect the CLI version independently.

Configurable options are executable name, timeout, optional model, explicit reasoning effort, and
explicit extra arguments. `reasoning_effort` is translated into the Codex CLI configuration key
`model_reasoning_effort`; supported repository values are `none`, `low`, `medium`, `high`, `xhigh`,
and `max`. The selected model is still responsible for supporting the requested effort.

A quality-first GPT-5.6 Sol production profile can therefore use:

```json
{
  "provider": "codex-cli",
  "provider_options": {
    "executable": "codex",
    "timeout_seconds": 3600,
    "model": "gpt-5.6-sol",
    "reasoning_effort": "xhigh",
    "extra_args": ["--sandbox", "workspace-write", "--ephemeral"]
  }
}
```

Because generation and review are separate provider calls, the same explicit model and reasoning
configuration applies independently to both invocations. Raw stdout/stderr and effective model /
reasoning provenance are kept inside the ignored local workspace for diagnosis and must not be
published without review.

The repository does not enable approval or sandbox bypasses by default.

## Extension points

Implement `AgentProvider.run`, return `AgentRunResult`, preserve isolated generation/review calls,
write a complete output artifact, and expose actual model/provider provenance. Placeholder provider
names fail loudly until an implementation exists.
