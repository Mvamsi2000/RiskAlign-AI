"""Schemas for MCP tool interactions."""
from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field


class ToolInvocation(BaseModel):
    """Represents a tool call request."""

    model_config = ConfigDict(extra="ignore")

    tool: str = Field(..., description="Tool identifier")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments supplied to the tool")


class ToolResult(BaseModel):
    """Represents a tool response."""

    model_config = ConfigDict(extra="ignore")

    tool: str = Field(..., description="Tool identifier")
    result: Dict[str, Any] = Field(default_factory=dict, description="Tool execution result payload")


__all__ = ["ToolInvocation", "ToolResult"]
