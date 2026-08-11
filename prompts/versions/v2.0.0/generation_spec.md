# Generation specification

Version: 2.0.0

This is the shared contract for both generation and independent review. Both agents author exactly
29 fields. The final 30th field, `meaning_merged`, is deterministic pipeline output.

## General serialization

- `first` is the consecutive global integer beginning at the first index shown in the rendered
  batch.
- `word` reproduces the lexical input exactly, including case, spaces, punctuation, and brackets.
- Every string field is non-empty. Use the literal em dash `—` (U+2014) for missing values; never
  use an empty string, null, `None`, or a hyphen.
- Simplified Chinese should be concise and natural. German forms and collocations should be
  idiomatic and useful to a learner.

## Spelling and grammar fields

- `spell_word`: put the exact headword first and separate useful accepted spellings with `/`.
  Expand genuinely optional bracketed material, but do not mix capitalization-distinct homographs
  or invent misspellings.
- `class` uses one label or a slash combination of: `N.`, `V.`, `Adj.`, `Adv.`, `Präp.`, `Konj.`,
  `Pron.`, `Art.`, `Num.`, `Int.`, `Part.`, `Abk.`, `Wend.`.
- `class_options` is determined from `class`: noun-like or `Abk.` → `N.`; verb → `V.`;
  any class containing `Adj.` → `Adj.`; `Wend.` → `Wend.`; all others → `others`.
- `change`: nouns use article and plural (`der, die Pläne`) or `nur Sg`/`Pl.`; verbs use third
  person present, preterite, and perfect (`läuft, lief, ist gelaufen`); adjectives use comparison
  when idiomatic; otherwise `—`.
- `pronunciation`: IPA in square brackets when reliable, otherwise `—`.
- `correct_option` begins with the exact `class` value, one space, then a concise Chinese summary.

## Meanings and collocations

- `meaning1` is mandatory. Unused later meaning slots are `—`.
- Each non-missing meaning includes an appropriate label: nouns `m./f./n./Pl.`, verbs
  `Vt./Vi./Vr./Vimp.`, and other classes their local label. Never use lowercase `v.`.
- Separate common learner-relevant senses into successive slots. Do not fill seven slots merely to
  avoid missing values.
- Each `collocationN` and `collocationN_translation` is a strict pair: both are `—`, or both are
  present and correspond to `meaningN`. Use `jdn.`, `jdm.`, `etw.(Akk)` and similar compact case
  notation where useful.
- No agent writes `meaning_merged`. At final merge, the pipeline inserts it immediately after
  `correct_option` as `；`.join of non-`—` `meaning1` through `meaning7`, preserving the complete
  meaning strings and their order.

## Difficult entries

- Preserve capitalization distinctions such as `recht` versus `Recht`.
- Expand optional spelling in `spell_word`, for example `(Rad-)Tour/Radtour/Tour`, only when the
  variants are genuine; do not alter `word`.
- Treat multiword lexical units as one entry. A multiword noun phrase remains `N.` rather than
  becoming `Wend.` merely because it contains spaces.
- Reflexive and separable verbs must show the pronoun and separated forms coherently in `change`.
- A supplied `expected_pos` identifies the intended homograph, but the output uses this local class
  system; composite classes remain valid when the entry genuinely has multiple functions.

Mechanical validation proves structure and selected invariants only. It does not establish
linguistic correctness; independent review and human sampling remain necessary.
