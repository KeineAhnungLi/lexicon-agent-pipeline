from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def exact_match(
    candidate: Sequence[Mapping[str, Any]],
    reference: Sequence[Mapping[str, Any]],
    fields: Sequence[str],
) -> dict[str, float | int]:
    if len(candidate) != len(reference):
        return {"matched": 0, "compared": max(len(candidate), len(reference)), "rate": 0.0}
    compared = len(candidate) * len(fields)
    matched = sum(
        candidate[index].get(field) == reference[index].get(field)
        for index in range(len(candidate))
        for field in fields
    )
    return {
        "matched": matched,
        "compared": compared,
        "rate": matched / compared if compared else 0.0,
    }
