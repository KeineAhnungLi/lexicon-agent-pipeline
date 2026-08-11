from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RubricCriterion:
    name: str
    description: str
    minimum: int = 0
    maximum: int = 2


DEFAULT_RUBRIC: tuple[RubricCriterion, ...] = (
    RubricCriterion("meaning", "Chinese meaning matches the selected German sense."),
    RubricCriterion("word_form", "Spelling, inflection, change, and pronunciation are accurate."),
    RubricCriterion("grammar", "Class and correct-option grammar are accurate and coherent."),
    RubricCriterion("collocation", "German collocations are idiomatic and support each sense."),
    RubricCriterion(
        "translation",
        "Each Chinese collocation translation naturally and faithfully matches its German text.",
    ),
)
