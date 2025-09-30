"""Auto detection utilities for the ingestion pipeline."""
from __future__ import annotations

from typing import Iterable, List, Tuple

from .base import IngestAdapter


def pick_adapter(adapters: Iterable[IngestAdapter], file_name: str, sample: bytes) -> Tuple[IngestAdapter, float]:
    """Return the adapter with the highest confidence score."""

    best: Tuple[IngestAdapter | None, float] = (None, 0.0)
    for adapter in adapters:
        score = adapter.confidence(file_name, sample)
        if score > best[1]:
            best = (adapter, score)
    if best[0] is None:
        raise ValueError("No suitable ingest adapter found for the supplied artifact")
    return best  # type: ignore[return-value]


def default_adapters() -> List[IngestAdapter]:
    """Instantiate the default adapters used by the pipeline."""

    from .log_text import LogTextAdapter
    from .nessus_xml import NessusXMLAdapter
    from .network_csv import NetworkCSVAdapter

    return [
        NessusXMLAdapter(),
        NetworkCSVAdapter(),
        LogTextAdapter(),
    ]


__all__ = ["pick_adapter", "default_adapters"]
