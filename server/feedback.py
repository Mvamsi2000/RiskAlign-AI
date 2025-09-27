"""Feedback ingestion utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List


@dataclass
class Feedback:
    """Represents stakeholder feedback on controls or narratives."""

    author: str
    message: str
    submitted_at: datetime


class FeedbackStore:
    """In-memory storage for feedback entries."""

    def __init__(self) -> None:
        self._entries: List[Feedback] = []

    def add(self, feedback: Feedback) -> None:
        self._entries.append(feedback)

    def list(self) -> List[Feedback]:
        return list(self._entries)

    def extend(self, items: Iterable[Feedback]) -> None:
        for item in items:
            self.add(item)


__all__ = [
    "Feedback",
    "FeedbackStore",
]
