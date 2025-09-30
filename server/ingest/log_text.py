"""Adapter for unstructured log or text files."""
from __future__ import annotations

import re
from typing import Iterable, List

from server.schemas import CanonicalFinding

from .base import IngestAdapter


_ALERT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"failed login",
        r"error",
        r"alert",
        r"critical",
        r"denied",
        r"unauthorized",
    ]
]


class LogTextAdapter(IngestAdapter):
    """Produces findings from unstructured security logs."""

    name = "log_text"
    extensions = (".log", ".txt")
    content_types = ("text/plain",)

    def confidence(self, file_name: str, sample: bytes) -> float:
        text = sample[:256].decode("utf-8", errors="ignore").lower()
        if any(keyword in text for keyword in ("ssh", "error", "failed")):
            return 0.7
        return super().confidence(file_name, sample)

    def parse(self, file_name: str, data: bytes) -> Iterable[CanonicalFinding]:
        text = self._ensure_unicode(data)
        findings: List[CanonicalFinding] = []
        for index, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            matched_keywords = [pattern.pattern for pattern in _ALERT_PATTERNS if pattern.search(line)]
            if not matched_keywords:
                continue
            findings.append(
                CanonicalFinding(
                    id=f"log-{index}",
                    title=f"Log alert line {index}",
                    description=line.strip(),
                    severity="medium" if "critical" not in line.lower() else "high",
                    tags=["log", *matched_keywords],
                )
            )
        return findings


__all__ = ["LogTextAdapter"]
