# Public data policy

Only data with a clear right to redistribute may be committed.

The public demo contains 15 entries newly authored for this repository from ordinary language
knowledge. They cover nouns, verbs, a reflexive and separable verb, adjective, adverbs, preposition,
conjunction, pronoun, fixed phrase, capitalization ambiguity, bracket notation, and an explicitly
context-dependent abbreviation. They are synthetic fixtures, not benchmark results and not
excerpts from the private production corpus.

The public synthetic examples, demo word list, and MockProvider fixtures are dedicated under
CC0-1.0 as specified in `DATA_LICENSE`. Code, prompts, and documentation are licensed under MIT.

Before adding data:

1. Record its origin, author, rights basis, intended use, and whether personal information exists.
2. Prefer a small synthetic fixture over a sample copied from production.
3. Remove machine paths, credentials, raw transcripts, customer/project identifiers, and metadata
   that could reveal a private source.
4. Do not commit source spreadsheets, licensed dictionaries, scraped corpora, full model outputs,
   or “anonymized” samples whose redistribution rights remain uncertain.
5. Run `lexicon-pipeline audit-public-release --root .` and review the result manually.

The automated audit is a guardrail, not legal advice or a complete copyright/privacy review.
