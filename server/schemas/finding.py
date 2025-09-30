from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, computed_field


def _severity_from_cvss(score: float | None) -> str:
    if score is None:
        return "unknown"
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "medium"
    if score > 0:
        return "low"
    return "informational"


class CanonicalAsset(BaseModel):
    """Minimal context about the affected asset."""

    name: Optional[str] = None
    kind: Optional[str] = None
    location: Optional[str] = None
    ip_address: Optional[str] = None


class CanonicalSignals(BaseModel):
    """Optional enrichment signals attached to the finding."""

    epss: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    kev: bool = False


class CanonicalFinding(BaseModel):
    """Normalised vulnerability finding used across the platform."""

    id: str = Field(description="Stable identifier for the finding within the batch")
    title: str = Field(description="Short human readable title")
    description: Optional[str] = Field(default=None, description="Detailed description from the source feed")
    severity: str = Field(default="unknown", description="Normalised qualitative severity label")
    cve: Optional[str] = Field(default=None, description="Associated CVE identifier if available")
    cvss: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    epss: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    kev: bool = Field(default=False, description="True when listed in CISA KEV catalogue")
    asset: Optional[CanonicalAsset] = None
    effort_hours: Optional[float] = Field(default=None, ge=0.0)
    observed_at: Optional[datetime] = Field(default=None, description="Timestamp when the issue was observed")
    source: Optional[str] = Field(default=None, description="Adapter that produced the finding")
    tags: List[str] = Field(default_factory=list)
    raw: Optional[Any] = Field(default=None, description="Raw source payload for traceability")
    signals: CanonicalSignals = Field(default_factory=CanonicalSignals)

    @computed_field  # type: ignore[misc]
    @property
    def effective_severity(self) -> str:
        """Return the severity, deriving it from CVSS if missing."""

        if self.severity and self.severity != "unknown":
            return self.severity
        if self.cvss is not None:
            return _severity_from_cvss(self.cvss)
        return "unknown"


__all__ = [
    "CanonicalAsset",
    "CanonicalSignals",
    "CanonicalFinding",
]
