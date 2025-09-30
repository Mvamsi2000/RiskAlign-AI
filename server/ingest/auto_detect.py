from __future__ import annotations

from typing import Iterable, Optional

from .base import AdapterBase
from .log_text import LogTextAdapter
from .nessus_xml import NessusXMLAdapter
from .network_csv import NetworkCSVAdapter

_ADAPTERS: Iterable[AdapterBase] = (
    NessusXMLAdapter(),
    NetworkCSVAdapter(),
    LogTextAdapter(),
)


def detect_adapter(content: bytes, filename: str | None = None) -> Optional[AdapterBase]:
    """Return the first adapter that can handle the payload."""

    for adapter in _ADAPTERS:
        try:
            if adapter.detect(content, filename):
                return adapter
        except Exception:
            continue
    return None


__all__ = ["detect_adapter"]
