"""Domain models describing canonical security findings used across the API."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AssetContext(BaseModel):
    """Describes the asset context associated with a finding."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    name: Optional[str] = Field(None, description="Asset identifier or hostname")
    criticality: Optional[str] = Field(
        None, description="Business criticality rating such as High, Medium, Low"
    )
    exposure: Optional[str] = Field(None, description="Exposure level such as Internet or Internal")
    data_sensitivity: Optional[str] = Field(
        None, description="Primary data classification handled by the asset"
    )


class CanonicalFinding(BaseModel):
    """Normalized representation of an analytic finding."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Unique identifier for the finding")
    title: str = Field(..., description="Short, human-readable title")
    description: Optional[str] = Field(None, description="Detailed narrative of the finding")
    cve: Optional[str] = Field(None, description="Associated CVE identifier when available")
    severity: Optional[str] = Field(None, description="Source severity label")
    cvss: Optional[float] = Field(
        None,
        ge=0,
        le=10,
        description="CVSS base score for the finding if provided by the source",
        alias="cvss_score",
    )
    epss: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Exploit Prediction Scoring System probability",
    )
    mvi: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Custom vendor or maturity index representing exploitability",
    )
    kev: bool = Field(False, description="Whether the issue is tracked in the CISA KEV catalog")
    detected_at: Optional[datetime] = Field(None, description="Timestamp when the finding was observed")
    asset: Optional[AssetContext] = Field(None, description="Impacted asset context")
    remediation: Optional[str] = Field(None, description="Suggested remediation guidance")
    references: list[str] = Field(default_factory=list, description="Relevant external references")
    tags: list[str] = Field(default_factory=list, description="Labels attached during ingestion")
    evidence: Optional[str] = Field(None, description="Evidence or raw data excerpt")
    effort_hours: Optional[float] = Field(
        None,
        ge=0,
        description="Estimated effort to remediate when provided by the source",
    )


__all__ = ["AssetContext", "CanonicalFinding"]
