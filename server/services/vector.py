"""Placeholder vector service."""
from __future__ import annotations

from typing import Any, List

from server.schemas import CanonicalFinding


def build_vector_index(findings: List[CanonicalFinding]) -> dict[str, Any]:
    """Return a stubbed in-memory vector index description."""
    return {"size": len(findings), "dimensions": 0}
