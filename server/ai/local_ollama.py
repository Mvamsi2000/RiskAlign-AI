"""Local deterministic AI provider used for development."""
from __future__ import annotations

from typing import Any, Dict, Optional


def _summarize(intent: str, result: Dict[str, Any]) -> str:
    if intent == "plan":
        waves = result.get("waves", [])
        total_risk = result.get("totals", {}).get("total_risk_saved", 0)
        return f"Generated {len(waves)} remediation waves saving {total_risk} risk units."
    if intent == "score":
        totals = result.get("totals", {})
        return (
            f"Scored {totals.get('count', 0)} findings with average score {totals.get('average_score', 0)}."
        )
    if intent == "impact":
        readiness = result.get("readiness_percent", 0)
        return f"Estimated readiness at {readiness}% with risk reduction curve prepared."
    if intent == "map":
        coverage = result.get("coverage", 0)
        return f"Mapped controls with {coverage}% coverage and {len(result.get('unique_controls', []))} matches."
    if intent == "summary":
        return "Executive summary generated and saved to disk."
    return "Handled request with local analytic heuristics."


async def chat(prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    context = context or {}
    intent = context.get("intent", "summary")
    result = context.get("result", {})
    return {
        "provider": "local",
        "intent": intent,
        "message": _summarize(intent, result),
        "matched_keywords": context.get("matched_keywords", []),
    }


__all__ = ["chat"]
