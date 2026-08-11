from __future__ import annotations

MISSING_VALUE = "—"

AGENT_FIELD_NAMES: tuple[str, ...] = (
    "first",
    "word",
    "spell_word",
    "class_options",
    "class",
    "change",
    "pronunciation",
    "correct_option",
    "meaning1",
    "collocation1",
    "collocation1_translation",
    "meaning2",
    "collocation2",
    "collocation2_translation",
    "meaning3",
    "collocation3",
    "collocation3_translation",
    "meaning4",
    "collocation4",
    "collocation4_translation",
    "meaning5",
    "collocation5",
    "collocation5_translation",
    "meaning6",
    "collocation6",
    "collocation6_translation",
    "meaning7",
    "collocation7",
    "collocation7_translation",
)

FINAL_FIELD_NAMES: tuple[str, ...] = (
    *AGENT_FIELD_NAMES[:8],
    "meaning_merged",
    *AGENT_FIELD_NAMES[8:],
)

# Backwards-compatible name for callers that mean the final public record.
FIELD_NAMES = FINAL_FIELD_NAMES

ALLOWED_CLASS_OPTIONS = frozenset({"N.", "V.", "Adj.", "others", "Wend."})
ALLOWED_CLASS_PARTS = frozenset(
    {
        "N.",
        "V.",
        "Adj.",
        "Adv.",
        "Präp.",
        "Postp.",
        "Konj.",
        "Pron.",
        "Art.",
        "Num.",
        "Int.",
        "Part.",
        "Abk.",
        "Wend.",
        "Kontr.",
    }
)

EXPECTED_POS_ALIASES = {
    "adj": "Adj.",
    "adjective": "Adj.",
    "adjektiv": "Adj.",
    "adv": "Adv.",
    "adverb": "Adv.",
    "art": "Art.",
    "article": "Art.",
    "artikel": "Art.",
    "intj": "Int.",
    "interjection": "Int.",
    "interjektion": "Int.",
    "conj": "Konj.",
    "conjunction": "Konj.",
    "konjunktion": "Konj.",
    "contr": "Kontr.",
    "contraction": "Kontr.",
    "kontraktion": "Kontr.",
    "n": "N.",
    "noun": "N.",
    "nomen": "N.",
    "substantiv": "N.",
    "num": "Num.",
    "numeral": "Num.",
    "numerale": "Num.",
    "part": "Part.",
    "particle": "Part.",
    "partikel": "Part.",
    "phr": "Wend.",
    "phrase": "Wend.",
    "postp": "Postp.",
    "postpos": "Postp.",
    "postposition": "Postp.",
    "prep": "Präp.",
    "preposition": "Präp.",
    "präposition": "Präp.",
    "praeposition": "Präp.",
    "pron": "Pron.",
    "pronoun": "Pron.",
    "pronomen": "Pron.",
    "v": "V.",
    "verb": "V.",
}
