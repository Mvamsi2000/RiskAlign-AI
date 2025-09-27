"""Mappings between frameworks and internal control references."""

from __future__ import annotations

from typing import Dict


class ControlMapping:
    """Stores mappings between different control frameworks."""

    def __init__(self) -> None:
        self._mapping: Dict[str, str] = {}

    def add_mapping(self, source: str, target: str) -> None:
        """Register a mapping between a source and target control."""
        self._mapping[source] = target

    def resolve(self, source: str) -> str | None:
        """Resolve a source control to its mapped target if available."""
        return self._mapping.get(source)


__all__ = [
    "ControlMapping",
]
