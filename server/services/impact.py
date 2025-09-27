from __future__ import annotations

from typing import Iterable

from ..schemas import Finding, ImpactEstimate, ImpactEstimateResponse


def estimate_impact(findings: Iterable[Finding]) -> ImpactEstimateResponse:
    total_risk = 0.0
    total_cost = 0.0
    compliance_gain = 0.0

    for finding in findings:
        risk_factor = finding.cvss + (finding.epss * 5) + (2 if finding.kev else 0)
        total_risk += risk_factor
        total_cost += (finding.asset_criticality * 25000) * (finding.epss + 0.2)
        compliance_gain += 4 if finding.data_sensitivity.value in {"confidential", "high"} else 2

    impact = ImpactEstimate(
        breach_cost=round(total_cost, 2),
        compliance_gain=round(min(compliance_gain, 100.0), 2),
        risk_reduction=round(total_risk * 0.3, 2),
    )
    return ImpactEstimateResponse(impact=impact)
