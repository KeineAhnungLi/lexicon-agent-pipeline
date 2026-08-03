# Agent independence

Generation and review are separate provider invocations. For Codex they are separate operating
system processes: the reviewer receives the rendered task and draft artifact, not the generator’s
conversation state. A self-check inside one response cannot satisfy this gate.

The primary orchestrator does not author records. It may delegate disjoint batch work where the
host supports subagents, but delegates must receive complete prompts and remain subject to the same
independent review and mechanical validation.

MockProvider uses two different fixture paths to exercise the control boundary without claiming
actual model independence or language quality. The generation fixture intentionally contains one
structurally valid semantic mismatch that the reviewed fixture corrects.
