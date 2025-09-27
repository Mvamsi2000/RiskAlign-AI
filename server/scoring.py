"""Scoring logic for translating assessment data into risk scores."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class ControlScore:
    """Represents the score for a single control."""

    control_id: str
    score: float
    weight: float = 1.0

    @property
    def weighted_score(self) -> float:
        """Return the weighted score contribution."""
        return self.score * self.weight


def aggregate_scores(scores: Iterable[ControlScore]) -> float:
    """Aggregate control scores into a single composite score."""
    total_weight = 0.0
    total_value = 0.0
    for control in scores:
        total_weight += control.weight
        total_value += control.weighted_score
    if total_weight == 0:
        return 0.0
    return total_value / total_weight


__all__ = [
    "ControlScore",
    "aggregate_scores",
]
