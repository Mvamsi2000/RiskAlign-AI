"""Domain models describing canonical security findings."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CanonicalFinding(BaseModel):
    """Normalized representation of an analytic finding."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Unique identifier for the finding")
    title: str = Field(..., description="Short, human-readable title")
    description: Optional[str] = Field(None, description="Detailed narrative of the finding")
    asset: Optional[str] = Field(None, description="The impacted asset or host")
    severity: Optional[str] = Field(None, description="Source severity label")
    cvss_score: Optional[float] = Field(
        None,
        ge=0,
        le=10,
        description="CVSS base score when provided by the source",
    )
    epss: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Exploit Prediction Scoring System probability",
    )
    kev: bool = Field(default=False, description="Whether the issue is tracked in the CISA KEV catalog")
    detected_at: Optional[datetime] = Field(None, description="Timestamp when the finding was observed")
    remediation: Optional[str] = Field(None, description="Suggested remediation guidance")
    references: list[str] = Field(default_factory=list, description="Relevant external references")
    tags: list[str] = Field(default_factory=list, description="Labels attached during ingestion")
    evidence: Optional[str] = Field(None, description="Evidence or raw data excerpt")
