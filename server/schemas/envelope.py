"""Schemas related to model control protocol (MCP) envelopes."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class MCPEnvelope(BaseModel):
    """Structured request envelope exchanged with MCP tooling."""

    model_config = ConfigDict(extra="ignore")

    intent: str = Field(..., description="High level intent of the natural language request")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Normalized payload supplied to the tool")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata generated during resolution")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier for the calling client")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the envelope was created")


__all__ = ["MCPEnvelope"]
