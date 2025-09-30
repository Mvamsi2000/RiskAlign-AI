"""Shared API-facing schemas."""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field

from .finding import CanonicalFinding


class ScoringWeights(BaseModel):
    """Relative weights applied to individual scoring dimensions."""

    model_config = ConfigDict(extra="forbid")

    cvss: float = Field(0.6, ge=0, description="Weight applied to CVSS scores")
    epss: float = Field(0.3, ge=0, description="Weight applied to EPSS probabilities")
    kev: float = Field(0.1, ge=0, description="Weight applied when a finding is on the KEV list")
    context: float = Field(0.0, ge=0, description="Custom context multiplier for future extensions")


class ScoringConfig(BaseModel):
    """Configuration payload accepted by the scoring engine."""

    model_config = ConfigDict(extra="ignore")

    max_score: float = Field(10.0, gt=0, description="Maximum risk score that may be returned")
    risk_tolerance: float = Field(7.5, ge=0, le=10, description="Threshold representing acceptable risk")
    weights: ScoringWeights = Field(default_factory=ScoringWeights, description="Weights for scoring dimensions")


class Wave(BaseModel):
    """Represents a remediation wave produced by the optimizer."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Human readable label for the wave")
    order: int = Field(..., ge=0, description="Zero-based index of the wave")
    capacity_hours: float = Field(..., ge=0, description="Effort budget assigned to the wave")
    findings: List[str] = Field(default_factory=list, description="Identifiers of findings scheduled in the wave")
    total_risk_reduction: float = Field(0.0, ge=0, description="Aggregate risk reduction achieved by the wave")
    estimated_effort_hours: float = Field(0.0, ge=0, description="Estimated effort to complete the wave")


__all__ = ["CanonicalFinding", "ScoringConfig", "Wave"]
