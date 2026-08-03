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
    RubricCriterion("grammar", "Forms and grammatical features are accurate and coherent."),
    RubricCriterion("example", "Example is idiomatic and supports the selected sense."),
    RubricCriterion("translation", "Translation naturally and faithfully matches the example."),
    RubricCriterion(
        "metadata",
        "Level, part of speech, register, region, and notes are appropriate.",
    ),
)
