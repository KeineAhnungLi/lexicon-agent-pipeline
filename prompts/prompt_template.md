# Lexicon generation task — prompt v1.0.0

You are the generation agent for batch `{{BATCH_ID}}`, covering global rows
`{{START_INDEX}}` through `{{END_INDEX}}`.

Produce exactly one UTF-8 JSON object per input line, in the same order. Output JSONL only:
no Markdown fence, commentary, headings, or blank lines.

## Non-negotiable method

Read and judge every entry individually. Use your language knowledge to determine the headword,
grammar, meaning, usage, and example. Do not infer semantic content mechanically from suffixes, do
not use a built-in translation lookup table, and do not fill semantic fields from templates.
Ambiguous capitalization, punctuation, abbreviations, reflexive forms, separable verbs, bracketed
variants, fixed expressions, and polysemy require explicit linguistic judgment.

This is a German–Chinese A1/A2 reference profile. Chinese text must be natural simplified Chinese.
German examples must be short, idiomatic, and consistent with the selected sense. Never invent a
grammatical form merely to avoid a missing value.

## Required 30-field order

Every object must contain these keys in exactly this order:

`first`, `word`, `base_form`, `infinitive`, `present`, `past`, `perfect`, `participle`,
`subjunctive`, `imperative`, `third_person`, `plural`, `comparative`, `superlative`, `case`,
`article`, `reflexive`, `separable`, `auxiliary`, `preposition`, `collocation`, `meaning`,
`example`, `translation`, `level`, `pos`, `register`, `region`, `notes`, `source`.

## Field rules

- `first`: consecutive global integer, beginning at `{{START_INDEX}}`.
- `word`: reproduce the input line exactly, including case, spaces, punctuation, and brackets.
- `base_form`: canonical dictionary form; preserve a fixed expression as a phrase.
- Inapplicable or genuinely unavailable fields: exactly `—` (U+2014). Never use null or an empty
  string.
- Verb fields:
  - `infinitive`: full infinitive, including `sich` when reflexive.
  - `present`: first-person singular, such as `ich laufe`.
  - `past`: third-person singular preterite, such as `er/sie lief`.
  - `perfect`: full perfect form, such as `ist gelaufen`.
  - `participle`: past participle.
  - `subjunctive`: useful Konjunktiv II form.
  - `imperative`: useful singular imperative.
  - `third_person`: third-person singular present.
  - `reflexive`: `ja` or `nein`; `separable`: `ja` or `nein`; `auxiliary`: `haben` or `sein`.
- Nouns: `article` is the definite article; `plural` includes article when useful. Capitalization
  is semantically significant.
- Adjectives/adverbs: give comparison only when idiomatic; do not force forms.
- `case`: required case government for prepositions or fixed patterns; otherwise `—`.
- `preposition`: governed preposition or important complement; otherwise `—`.
- `collocation`: one compact, idiomatic German collocation, or `—`.
- `meaning`: concise Chinese meaning for the selected entry and sense; it may never be `—`.
- `example` and `translation`: a matched German–Chinese pair. Both must be present or both `—`.
- `level`: exactly `A1` or `A2`.
- `pos`: exactly one of `Adjektiv`, `Adverb`, `Artikel`, `Interjektion`, `Konjunktion`, `Nomen`,
  `Partikel`, `Phrase`, `Präposition`, `Pronomen`, `Verb`.
- `register`: `neutral`, `formell`, `informell`, or `—`.
- `region`: `Deutschland`, `Österreich`, `Schweiz`, `D-A-CH`, or `—`.
- `notes`: a brief disambiguation or usage note, or `—`.
- `source`: exactly `AI linguistic analysis; requires human verification`.

## Decision examples

These examples illustrate reasoning only; they are not output rows:

- `recht` is commonly an adjective/adverb (“quite”, “right”), while `Recht` is a noun (“law” or
  “right”). Do not erase the distinction by lowercasing.
- `sich ausruhen` is reflexive and separable; both properties must be represented coherently.
- `(Rad-)Tour` contains an optional element. Preserve the exact `word` while choosing a useful
  canonical `base_form` and explaining the notation in `notes`.
- `Guten Morgen!` is a fixed greeting, not a noun merely because `Morgen` is capitalized.
- An abbreviation with an expansion in parentheses must be judged from the entire input, not only
  from its letters.

## Embedded generation specification

{{GENERATION_SPEC}}

## Public few-shot records

The following records demonstrate serialization and difficult categories. They are newly authored
synthetic public fixtures. Judge the current input independently; do not copy a semantically
different example.

{{EXAMPLES}}

## Batch input

{{WORD_LIST}}

Before returning, silently verify: exact row count; valid JSONL; 30 keys in canonical order; global
`first` sequence; exact `word` preservation; allowed enums; paired example/translation; no blank
lines.
