from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping

from .scoring import score_compute


PlanWave = Dict[str, Any]
PlanResponse = Dict[str, Any]


def _normalise_hours(value: Any) -> float:
    try:
        hours = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(hours, 0.0)


def _risk_saved(score: float, priority: str) -> float:
    priority_boosts = {
        "Critical": 1.25,
        "High": 1.1,
        "Medium": 1.0,
        "Low": 0.8,
    }
    return round(score * priority_boosts.get(priority, 1.0), 2)


def optimize_plan(
    findings: Iterable[Mapping[str, Any]],
    *,
    max_hours_per_wave: float = 16.0,
    scored: Iterable[Mapping[str, Any]] | None = None,
    config: Mapping[str, Any] | None = None,
) -> PlanResponse:
    """Build remediation waves using a greedy risk-per-hour heuristic."""

    finding_list = list(findings)

    if scored is None:
        scored_payload = score_compute(finding_list, cfg=config)
        scored_items = scored_payload["findings"]
    else:
        scored_items = list(scored)

    enriched: List[Dict[str, Any]] = []
    for scored_item in scored_items:
        hours = _normalise_hours(scored_item.get("effort_hours"))
        if hours == 0.0:
            hours = 1.0
        score = float(scored_item.get("score", 0.0))
        priority = str(scored_item.get("priority", "Unclassified"))
        risk = _risk_saved(score, priority)
        ratio = risk / hours if hours else float("inf")
        enriched.append(
            {
                "id": scored_item.get("id"),
                "title": scored_item.get("title"),
                "effort_hours": round(hours, 2),
                "score": round(score, 2),
                "priority": priority,
                "risk_saved": risk,
                "ratio": ratio,
            }
        )

    enriched.sort(key=lambda item: (item["ratio"], item["risk_saved"]), reverse=True)

    waves: List[PlanWave] = []
    current_items: List[Dict[str, Any]] = []
    current_hours = 0.0
    current_risk = 0.0
    wave_index = 1

    for item in enriched:
        hours = item["effort_hours"]
        if current_items and current_hours + hours > max_hours_per_wave:
            waves.append(
                {
                    "name": f"Wave {wave_index}",
                    "total_hours": round(current_hours, 2),
                    "risk_saved": round(current_risk, 2),
                    "items": current_items,
                }
            )
            current_items = []
            current_hours = 0.0
            current_risk = 0.0
            wave_index += 1

        current_items.append(
            {
                "id": item["id"],
                "title": item["title"],
                "effort_hours": item["effort_hours"],
                "score": item["score"],
                "risk_saved": item["risk_saved"],
                "priority": item["priority"],
            }
        )
        current_hours += hours
        current_risk += item["risk_saved"]

    if current_items:
        waves.append(
            {
                "name": f"Wave {wave_index}",
                "total_hours": round(current_hours, 2),
                "risk_saved": round(current_risk, 2),
                "items": current_items,
            }
        )

    totals = {
        "waves": len(waves),
        "total_hours": round(sum(wave["total_hours"] for wave in waves), 2),
        "total_risk_saved": round(sum(wave["risk_saved"] for wave in waves), 2),
    }

    return {"waves": waves, "totals": totals}
