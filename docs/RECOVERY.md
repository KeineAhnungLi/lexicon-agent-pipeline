# Recovery and idempotency

Manifest state alone is never trusted. Recovery validates artifacts with the 29-field agent
contract. In full mode, a valid reviewed artifact is complete and a valid generated artifact resumes
at review. In simple mode, a valid generated artifact is complete enough to merge. Invalid files are
not mergeable.

Manifest v2 records `contract_version`, `agent_schema_hash`, and `final_schema_hash`. A manifest v1
belongs to the pre-2.0 contract and must be replaced by running `prepare`; old artifacts are not
silently resumed.

Writes that establish durable state use atomic replacement. Provider retries may differ, so hashes
and timestamps preserve provenance. Token totals are recorded only when exact values are available;
missing values remain explicitly unavailable.
