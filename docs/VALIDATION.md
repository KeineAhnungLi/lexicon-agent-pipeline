# Validation boundary

Mechanical validation checks UTF-8 readability, JSONL syntax, one object per row, exact row count,
30 keys in canonical serialized order, field types, global `first` sequence, byte-for-text `word`
alignment, enum allow-lists, required meaning, and the example/translation pair. Merge repeats all
batch checks and the global sequence.

It does not determine noun gender, plural, conjugation, pronunciation, meaning, sense coverage,
collocation naturalness, translation, or CEFR level. Those are agent/Judge/human evaluation
questions. Therefore reports use “mechanical validation PASS,” never “semantic accuracy.”

On a stage validation failure the same stage may be invoked again with the validator report, up to
the configured attempt limit. The program does not patch semantic fields itself.
