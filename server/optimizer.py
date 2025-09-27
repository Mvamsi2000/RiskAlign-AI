"""Optimization helpers for prioritizing remediation tasks."""

from __future__ import annotations

from typing import Iterable, Sequence

from .scoring import ControlScore


def prioritize_controls(scores: Iterable[ControlScore]) -> list[ControlScore]:
    """Return controls ordered by impact (highest score first)."""
    return sorted(scores, key=lambda item: item.score, reverse=True)


def select_top_controls(scores: Sequence[ControlScore], limit: int = 5) -> list[ControlScore]:
    """Select the top N controls for focus."""
    if limit <= 0:
        return []
    return list(prioritize_controls(scores)[:limit])


__all__ = [
    "prioritize_controls",
    "select_top_controls",
]
