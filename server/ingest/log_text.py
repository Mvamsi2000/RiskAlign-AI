from __future__ import annotations

from datetime import datetime
from typing import Iterable, Iterator

from .base import AdapterBase
from ..schemas import CanonicalFinding


class LogTextAdapter(AdapterBase):
    slug = "log_text"
    label = "Log Indicators"
    supported_extensions = (".log", ".txt")

    def detect(self, content: bytes, filename: str | None = None) -> bool:
        filename = filename or ""
        if any(filename.lower().endswith(ext) for ext in self.supported_extensions):
            return True
        head = content[:128].decode("utf-8", errors="ignore")
        return "indicator" in head.lower()

    def parse(self, content: bytes) -> Iterable[str]:
        text = content.decode("utf-8", errors="ignore")
        return [line.strip() for line in text.splitlines() if line.strip()]

    def map(self, parsed: Iterable[str]) -> Iterable[CanonicalFinding]:
        return list(self._iter_findings(parsed))

    def _iter_findings(self, lines: Iterable[str]) -> Iterator[CanonicalFinding]:
        for index, line in enumerate(lines, start=1):
            severity = "low"
            if "critical" in line.lower():
                severity = "high"
            elif "warning" in line.lower():
                severity = "medium"

            yield CanonicalFinding(
                id=f"log-{index}",
                title=line[:120],
                description=line,
                severity=severity,
                source=self.slug,
                observed_at=datetime.utcnow(),
                tags=["log", "indicator"],
            )


__all__ = ["LogTextAdapter"]
