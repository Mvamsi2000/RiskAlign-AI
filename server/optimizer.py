from __future__ import annotations

from typing import List

from .scoring import compute_scores
from .schemas import Finding, OptimizePlanRequest, OptimizePlanResponse, RemediationWave, WaveItem


def optimize_plan(request: OptimizePlanRequest) -> OptimizePlanResponse:
    scores = compute_scores(request.findings)
    ranked = []
    for scored, finding in zip(scores.results, request.findings):
        effort = finding.effort_hours or 4.0
        risk_reduction = round(scored.score * 0.8, 2)
        ranked.append((scored, effort, risk_reduction))

    ranked.sort(key=lambda item: item[0].score / max(item[1], 1e-3), reverse=True)

    waves: List[RemediationWave] = []
    current_wave: List[WaveItem] = []
    current_hours = 0.0
    wave_index = 1

    for scored, effort, risk_reduction in ranked:
        if current_hours + effort > request.max_hours_per_wave and current_wave:
            waves.append(
                RemediationWave(
                    name=f"Wave {wave_index}",
                    total_hours=round(current_hours, 2),
                    expected_risk_reduction=round(sum(item.risk_reduction for item in current_wave), 2),
                    items=current_wave,
                )
            )
            current_wave = []
            current_hours = 0.0
            wave_index += 1

        current_wave.append(
            WaveItem(
                id=scored.id,
                title=scored.title,
                effort_hours=round(effort, 2),
                score=scored.score,
                risk_reduction=risk_reduction,
            )
        )
        current_hours += effort

    if current_wave:
        waves.append(
            RemediationWave(
                name=f"Wave {wave_index}",
                total_hours=round(current_hours, 2),
                expected_risk_reduction=round(sum(item.risk_reduction for item in current_wave), 2),
                items=current_wave,
            )
        )

    return OptimizePlanResponse(waves=waves)
