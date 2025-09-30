"""Greedy remediation plan generator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from server.schemas import (
    OptimizePlanRequest,
    OptimizePlanResponse,
    PlanItem,
    PlanTotals,
    RemediationWave,
    ScoreFinding,
)


@dataclass
class _QueueItem:
    finding: ScoreFinding
    ratio: float
    effort: float
    risk_saved: float


def _prepare_queue(findings: Iterable[ScoreFinding]) -> List[_QueueItem]:
    queue: List[_QueueItem] = []
    for finding in findings:
        score = getattr(finding, "score", 0.0) or 0.0
        effort = getattr(finding, "effort_hours", None)
        if effort is None or effort <= 0:
            effort = max(2.0, 12.0 - score)
        risk_saved = getattr(finding, "risk_saved", None)
        if risk_saved is None or risk_saved <= 0:
            risk_saved = max(score - 6.0, 0.0) * 1.1 or score * 0.6
        ratio = risk_saved / effort if effort else risk_saved
        queue.append(_QueueItem(finding=finding, ratio=ratio, effort=effort, risk_saved=risk_saved))
    queue.sort(key=lambda item: (item.ratio, item.risk_saved, item.finding.score), reverse=True)
    return queue


def _new_wave(index: int) -> RemediationWave:
    return RemediationWave(name=f"Wave {index}", total_hours=0.0, risk_saved=0.0, items=[])


def generate_plan(payload: OptimizePlanRequest) -> OptimizePlanResponse:
    """Generate a greedy remediation plan."""

    queue = _prepare_queue(payload.findings)
    if not queue:
        return OptimizePlanResponse(waves=[], totals=PlanTotals(), unassigned=[])

    max_hours = payload.max_hours_per_wave or 16.0
    waves: List[RemediationWave] = []
    unassigned: List[str] = []

    wave_index = 1
    current_wave = _new_wave(wave_index)

    for item in queue:
        if current_wave.total_hours + item.effort <= max_hours:
            current_wave.total_hours += item.effort
            current_wave.risk_saved += item.risk_saved
            current_wave.items.append(
                PlanItem(
                    id=item.finding.id,
                    title=item.finding.title,
                    priority=item.finding.priority,
                    effort_hours=round(item.effort, 2),
                    score=round(item.finding.score, 2),
                    risk_saved=round(item.risk_saved, 2),
                )
            )
        else:
            if current_wave.items:
                waves.append(current_wave)
                wave_index += 1
                current_wave = _new_wave(wave_index)
            if item.effort > max_hours * 1.5:
                unassigned.append(item.finding.id or "")
                continue
            current_wave.total_hours += item.effort
            current_wave.risk_saved += item.risk_saved
            current_wave.items.append(
                PlanItem(
                    id=item.finding.id,
                    title=item.finding.title,
                    priority=item.finding.priority,
                    effort_hours=round(item.effort, 2),
                    score=round(item.finding.score, 2),
                    risk_saved=round(item.risk_saved, 2),
                )
            )

    if current_wave.items:
        waves.append(current_wave)

    while len(waves) < payload.minimum_waves:
        wave_index = len(waves) + 1
        waves.append(_new_wave(wave_index))

    totals = PlanTotals(
        waves=len(waves),
        total_hours=round(sum(wave.total_hours for wave in waves), 2),
        total_risk_saved=round(sum(wave.risk_saved for wave in waves), 2),
    )

    return OptimizePlanResponse(waves=waves, totals=totals, unassigned=[uid for uid in unassigned if uid])


__all__ = ["generate_plan"]
