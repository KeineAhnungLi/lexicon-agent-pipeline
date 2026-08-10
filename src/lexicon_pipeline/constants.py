from __future__ import annotations

FIELD_NAMES: tuple[str, ...] = (
    "first",
    "word",
    "base_form",
    "infinitive",
    "present",
    "past",
    "perfect",
    "participle",
    "subjunctive",
    "imperative",
    "third_person",
    "plural",
    "comparative",
    "superlative",
    "case",
    "article",
    "reflexive",
    "separable",
    "auxiliary",
    "preposition",
    "collocation",
    "meaning",
    "example",
    "translation",
    "level",
    "pos",
    "register",
    "region",
    "notes",
    "source",
)

MISSING_VALUE = "—"
ALLOWED_LEVELS = frozenset({"A1", "A2"})
ALLOWED_POS = frozenset(
    {
        "Adjektiv",
        "Adverb",
        "Artikel",
        "Interjektion",
        "Konjunktion",
        "Kontraktion",
        "Nomen",
        "Numerale",
        "Partikel",
        "Phrase",
        "Postposition",
        "Präposition",
        "Pronomen",
        "Verb",
    }
)
ALLOWED_REGISTER = frozenset({"neutral", "formell", "informell", MISSING_VALUE})
ALLOWED_REGIONS = frozenset({"Deutschland", "Österreich", "Schweiz", "D-A-CH", MISSING_VALUE})
