"""Base classes for ingest adapters."""
from __future__ import annotations

import abc
from typing import Iterable, Sequence

from server.schemas import CanonicalFinding


class IngestAdapter(abc.ABC):
    """Base interface implemented by all artifact adapters."""

    name: str = "generic"
    extensions: Sequence[str] = ()
    content_types: Sequence[str] = ()

    def confidence(self, file_name: str, sample: bytes) -> float:
        """Return a score between 0 and 1 describing how confident the adapter is."""

        for extension in self.extensions:
            if file_name.lower().endswith(extension.lower()):
                return 0.9
        if any(content_type in (file_name or "").lower() for content_type in self.content_types):
            return 0.6
        return 0.0

    @abc.abstractmethod
    def parse(self, file_name: str, data: bytes) -> Iterable[CanonicalFinding]:
        """Parse the provided bytes into canonical findings."""

    def _ensure_unicode(self, data: bytes) -> str:
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("latin-1", errors="replace")


__all__ = ["IngestAdapter"]
