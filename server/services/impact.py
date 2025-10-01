"""Impact analytics derived from remediation plans."""
from __future__ import annotations

from typing import List

from server.schemas import ImpactEstimateResponse, ImpactRequest, MappingRequest, RiskCurvePoint

from . import mapping as mapping_service


def estimate_impact(payload: ImpactRequest) -> ImpactEstimateResponse:
    """Estimate readiness and compliance uplift based on the current plan."""

    total_risk_saved = sum(wave.risk_saved for wave in payload.waves)
    total_score = sum(finding.score for finding in payload.findings) or 1.0
    readiness = min(100.0, (total_risk_saved / total_score) * 100 if total_score else 0.0)
    residual = max(0.0, 100.0 - readiness)

    curve: List[RiskCurvePoint] = []
    cumulative = 0.0
    for wave in payload.waves:
        cumulative += wave.risk_saved
        percent = (cumulative / total_risk_saved * 100) if total_risk_saved else 0.0
        curve.append(
            RiskCurvePoint(
                wave=wave.name,
                cumulative_risk_saved=round(cumulative, 2),
                percent_of_total=round(min(percent, 100.0), 2),
            )
        )

    mapping = mapping_service.map_to_controls(
        MappingRequest(findings=payload.findings, framework=payload.framework)
    )

    compliance_boost = min(100.0, mapping.coverage + readiness * 0.25)

    return ImpactEstimateResponse(
        readiness_percent=round(readiness, 2),
        compliance_boost=round(compliance_boost, 2),
        residual_risk=round(residual, 2),
        risk_saved_curve=curve,
        controls_covered=mapping.unique_controls,
    )


__all__ = ["estimate_impact"]
