from __future__ import annotations

import random
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def deterministic_sample(items: Sequence[T], size: int, seed: int = 0) -> list[T]:
    if size < 0:
        raise ValueError("sample size must be non-negative")
    generator = random.Random(seed)
    return generator.sample(list(items), min(size, len(items)))
