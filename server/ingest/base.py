from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Sequence

from ..schemas import CanonicalFinding


class AdapterBase(ABC):
    """Common interface that ingestion adapters must implement."""

    slug: str = "base"
    label: str = "Base Adapter"
    supported_extensions: Sequence[str] = ()

    @abstractmethod
    def detect(self, content: bytes, filename: str | None = None) -> bool:
        """Return True if this adapter can handle the payload."""

    @abstractmethod
    def parse(self, content: bytes) -> object:
        """Parse the source bytes into an intermediate representation."""

    @abstractmethod
    def map(self, parsed: object) -> Iterable[CanonicalFinding]:
        """Yield canonical findings from the parsed payload."""


__all__ = ["AdapterBase"]
