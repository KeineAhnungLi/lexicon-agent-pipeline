# Recovery and idempotency

The manifest and validated artifacts jointly determine recovery. State labels alone are never
trusted. A valid reviewed batch is idempotently skipped. A valid generated-only batch proceeds
directly to review. Invalid artifacts are not merged.

Output and report files use atomic replacement where they establish durable state. The manifest is
saved after each completed stage. A process interruption can therefore require replaying at most
the current unfinished provider stage.

Provider calls themselves are not assumed idempotent: a repeated model call may produce different
language content. Hashes and timestamps make those differences traceable. Preserve failed local
artifacts for diagnosis, but do not publish raw transcripts.
