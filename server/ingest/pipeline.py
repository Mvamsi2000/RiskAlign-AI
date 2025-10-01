"""Ingestion pipeline orchestration."""
from __future__ import annotations

from typing import Iterable, List, Tuple

from server.schemas import CanonicalFinding, MCPEnvelope

from .auto_detect import default_adapters, pick_adapter
from .base import IngestAdapter

IngestResult = Tuple[List[CanonicalFinding], MCPEnvelope]


def run_ingest_pipeline(
    file_name: str,
    data: bytes,
    adapters: Iterable[IngestAdapter] | None = None,
) -> IngestResult:
    """Detect the appropriate adapter, parse findings and return an MCP envelope."""

    adapters = list(adapters or default_adapters())
    if not adapters:
        raise ValueError("No ingest adapters registered")

    adapter, confidence = pick_adapter(adapters, file_name, data[:512])
    findings = list(adapter.parse(file_name, data))

    envelope = MCPEnvelope(
        intent="ingest",
        payload={
            "source": file_name,
            "adapter": adapter.name,
            "findings": [finding.model_dump(mode="json") for finding in findings],
        },
        metadata={
            "confidence": confidence,
            "count": len(findings),
        },
    )

    return findings, envelope


__all__ = ["run_ingest_pipeline", "IngestResult"]
