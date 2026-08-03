from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


def summarize_judgments(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Aggregate supplied judgments without inventing missing observations."""
    labels = Counter(str(record.get("label", "unlabeled")) for record in records)
    severe = sum(record.get("severity") == "major" for record in records)
    human_verified = sum(bool(record.get("human_verified")) for record in records)
    total = len(records)
    return {
        "records": total,
        "label_counts": dict(labels),
        "major_error_rate": severe / total if total else None,
        "human_verified_records": human_verified,
        "notice": "Metrics summarize only the supplied evaluation records.",
    }
