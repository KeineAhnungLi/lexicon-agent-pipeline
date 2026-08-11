# German Classics lexicon generation — prompt v2.0.0

You are the generation agent for batch `{{BATCH_ID}}`, global rows `{{START_INDEX}}` through
`{{END_INDEX}}`.

Write exactly one UTF-8 JSON object per input row, in the same order. Output JSONL only: no
Markdown fence, heading, commentary, array wrapper, comma between records, or blank line.

## Method boundary

Read and judge every entry individually. Determine its spelling variants, grammatical class,
inflection, learner-facing Chinese meanings, and useful German collocations through linguistic
judgment. Never create semantic content through suffix guesses, lookup tables, copied neighboring
records, or templates. Preserve capitalization and distinguish homographs.

Do not generate examples or sentences. Do not output `meaning_merged`; the pipeline derives it
after the selected agent artifact has passed validation.

## Input identity

Each input line begins with the global index and lexical word. It may end with metadata such as
`[expected_pos=verb]`. Copy only the lexical word into `word`; never copy metadata into it.
Treat a supplied POS hint as a disambiguation constraint, while expressing the result in the local
`class` vocabulary. For example, adjective/adverb polyfunction may be `Adj./Adv.`; a contraction
may require a linguistically accurate combination such as `Präp./Art.`; postposed adpositions use
`Präp.` and must be represented by an idiomatic postposed collocation. Do not invent a new class
label merely by translating the input hint.

## Required agent contract: exactly 29 ordered keys

`first`, `word`, `spell_word`, `class_options`, `class`, `change`, `pronunciation`,
`correct_option`, `meaning1`, `collocation1`, `collocation1_translation`, `meaning2`,
`collocation2`, `collocation2_translation`, `meaning3`, `collocation3`,
`collocation3_translation`, `meaning4`, `collocation4`, `collocation4_translation`, `meaning5`,
`collocation5`, `collocation5_translation`, `meaning6`, `collocation6`,
`collocation6_translation`, `meaning7`, `collocation7`, `collocation7_translation`.

There is no `meaning_merged`, example, sentence, source, level, register, or region key in an agent
artifact.

## Embedded specification

{{GENERATION_SPEC}}

## Public synthetic serialization examples

{{EXAMPLES}}

These examples demonstrate format only. Judge every current input independently.

## Batch input

{{WORD_LIST}}

Before finishing, silently check: exact row count; valid JSONL; exactly 29 keys in canonical order;
continuous global `first`; byte-for-text `word` identity; no `meaning_merged` or example fields;
valid class mapping; at least `meaning1`; paired collocations and translations; no blank lines.
