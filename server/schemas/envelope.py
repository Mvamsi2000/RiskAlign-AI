from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field

from .finding import CanonicalFinding


class MCPEnvelope(BaseModel):
    """Envelope wrapper used for canonical finding JSONL exports."""

    schema: str = Field(default="https://riskalign.ai/mcp/envelope.json")
    kind: str = Field(default="canonical_finding")
    namespace: str = Field(description="Namespace associated with this batch")
    adapter: str = Field(description="Adapter identifier that produced the finding")
    received_at: datetime = Field(default_factory=datetime.utcnow)
    data: CanonicalFinding = Field(description="Canonical finding payload")
    meta: Dict[str, Any] = Field(default_factory=dict)


__all__ = ["MCPEnvelope"]
