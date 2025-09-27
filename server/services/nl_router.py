from __future__ import annotations

from typing import Dict, Iterable

from ..schemas import Finding, NaturalLanguageQueryResponse
from .optimizer import build_optimization_plan
from .scoring import compute_scores


INTENT_KEYWORDS = {
    "quick win": "quick_wins",
    "quick wins": "quick_wins",
    "plan": "plan_overview",
    "wave": "plan_overview",
    "controls": "controls",
    "compliance": "controls",
    "score": "scores",
    "priorit": "scores",
}


def handle_nl_query(query: str, findings: Iterable[Finding], config: Dict) -> NaturalLanguageQueryResponse:
    normalized = query.lower()
    intent = "summary"
    for keyword, mapped_intent in INTENT_KEYWORDS.items():
        if keyword in normalized:
            intent = mapped_intent
            break

    if intent == "quick_wins":
        plan = build_optimization_plan(findings, config, constraints=None)
        quick = [item for item in plan.plan if item.estimated_hours <= 10][:3]
        result = {
            "headline": "Top quick wins under 10 hours",
            "items": "\n".join(f"Wave {item.wave}: {item.title} ({item.estimated_hours}h)" for item in quick)
            or "No remediation items fit the quick win criteria.",
        }
    elif intent == "plan_overview":
        plan = build_optimization_plan(findings, config, constraints=None)
        result = {
            "headline": "Optimization plan overview",
            "items": "\n".join(
                f"Wave {item.wave}: {item.title} — {item.estimated_hours}h, risk Δ {item.expected_risk_reduction}"
                for item in plan.plan
            ),
        }
    elif intent == "controls":
        covered = [finding.cve for finding in findings if finding.cve]
        result = {
            "headline": "Controls mapping",
            "items": "\n".join(covered) or "No CVEs supplied to map against controls.",
        }
    else:
        scores = compute_scores(findings, config)
        top = sorted(scores.findings, key=lambda item: item.score, reverse=True)[:3]
        result = {
            "headline": "Top prioritized findings",
            "items": "\n".join(
                f"{item.finding.title} — priority {item.priority}, score {item.score}" for item in top
            ),
        }

    return NaturalLanguageQueryResponse(intent=intent, result=result)
