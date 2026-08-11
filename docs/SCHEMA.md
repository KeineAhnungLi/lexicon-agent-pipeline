# Record contracts

Contract 2.0.0 has two serialized record shapes.

The agent record contains exactly 29 ordered keys: eight identity/grammar fields followed by seven
`meaningN`, `collocationN`, `collocationN_translation` groups. Generation and review artifacts both
use `schemas/lexicon_agent_record.schema.json`. They contain neither `meaning_merged` nor examples.

The final record contains exactly 30 ordered keys. `meaning_merged` appears immediately after
`correct_option` and equals the full-width-semicolon join of every non-`—` meaning in numeric order.
The merger derives it; agents never author it. Final files use `schemas/lexicon_record.schema.json`.

JSON Schema checks shape and values but cannot enforce serialized key order or a derived equality.
The Python validator enforces those invariants. Empty strings and null are rejected; use the literal
em dash `—`. `meaning1` is mandatory, and every collocation/translation pair is jointly present or
jointly missing.
