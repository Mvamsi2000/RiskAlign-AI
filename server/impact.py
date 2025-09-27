from __future__ import annotations

from typing import Set

from .config_loader import controls_mapping
from .scoring import compute_scores
from .schemas import ImpactEstimateRequest, ImpactEstimateResponse


def estimate_impact(request: ImpactEstimateRequest) -> ImpactEstimateResponse:
    scores = compute_scores(request.findings)
    total_score = sum(result.score for result in scores.results)
    total_hours = sum((finding.effort_hours or 4.0) for finding in request.findings)

    breach_reduction = min(total_score * 1.5, 95.0)

    covered_controls: Set[str] = set()
    mapping = controls_mapping()
    for finding in request.findings:
        if not finding.cve:
            continue
        for control in mapping.get(finding.cve, []):
            covered_controls.add(control["control"])

    compliance_gain = min(len(covered_controls) * 6.0 + total_score * 0.4, 100.0)

    rationale = (
        f"Addressing {len(request.findings)} findings (~{total_hours:.1f} hours) "
        f"removes roughly {breach_reduction:.0f}% of modeled breach exposure and "
        f"advances {len(covered_controls)} CIS controls."
    )

    return ImpactEstimateResponse(
        breach_reduction=round(breach_reduction, 2),
        compliance_gain=round(compliance_gain, 2),
        rationale=rationale,
    )
