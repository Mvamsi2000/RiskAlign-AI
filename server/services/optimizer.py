from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from ..schemas import (
    Finding,
    OptimizationConstraint,
    OptimizationPlanResponse,
    RemediationItem,
)
from .scoring import compute_scores


def build_optimization_plan(
    findings: Iterable[Finding],
    config: Dict,
    constraints: Optional[OptimizationConstraint],
) -> OptimizationPlanResponse:
    scoring_response = compute_scores(findings, config)
    scored = sorted(
        scoring_response.findings,
        key=lambda item: (item.score / (item.finding.effort_hours or 1)),
        reverse=True,
    )

    max_hours = constraints.max_hours if constraints else None
    waves = constraints.waves if constraints else 3

    plan: List[RemediationItem] = []
    total_hours = 0.0
    total_reduction = 0.0

    for index, item in enumerate(scored):
        hours = item.finding.effort_hours or 0
        if max_hours is not None and total_hours + hours > max_hours:
            continue

        wave = (index % waves) + 1
        reduction = round(item.score * 0.15, 2)

        plan.append(
            RemediationItem(
                finding_id=item.finding.id,
                title=item.finding.title,
                wave=wave,
                estimated_hours=round(hours, 2),
                score=item.score,
                expected_risk_reduction=reduction,
            )
        )

        total_hours += hours
        total_reduction += reduction

    summary = (
        f"Prioritized {len(plan)} findings across {waves} wave(s) for roughly {total_hours:.1f} hours "
        f"of work, delivering an estimated {total_reduction:.1f} risk reduction points."
    )

    return OptimizationPlanResponse(plan=plan, summary=summary)
