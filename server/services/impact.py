"""Placeholder impact estimation service."""
from __future__ import annotations

from typing import List

from server.schemas.api import ImpactRequest, ImpactResponse, ImpactPoint


def estimate_impact(payload: ImpactRequest) -> ImpactResponse:
    """Return a deterministic impact estimate for the supplied plan."""
    if not payload.waves:
        return ImpactResponse(readiness_pct=0.0, residual_risk=100.0, risk_saved_curve=[])

    step = 100.0 / max(len(payload.waves), 1)
    curve: List[ImpactPoint] = [
        ImpactPoint(label=wave.name, risk_reduction=step * (index + 1))
        for index, wave in enumerate(payload.waves)
    ]
    readiness = min(step * len(payload.waves), 100.0)
    residual = max(0.0, 100.0 - readiness)

    return ImpactResponse(readiness_pct=readiness, residual_risk=residual, risk_saved_curve=curve)
