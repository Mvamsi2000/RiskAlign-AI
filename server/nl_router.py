from __future__ import annotations

from typing import Dict

from .schemas import NLQueryRequest, NLQueryResponse

_INTENT_HINTS: Dict[str, str] = {
    "optimize": "quick win budget hours wave plan priority",
    "compliance": "control coverage cis nist iso",
    "impact": "breach cost exposure reduction",
    "summary": "executive summary board",
}


def route_query(request: NLQueryRequest) -> NLQueryResponse:
    text = request.query.lower()
    intent = "general"
    confidence = 0.25

    for candidate, keywords in _INTENT_HINTS.items():
        hits = sum(1 for keyword in keywords.split() if keyword in text)
        score = hits / max(len(keywords.split()), 1)
        if score > confidence:
            intent = candidate
            confidence = score

    responses = {
        "optimize": "I'll prioritize remediation waves balancing risk-reduction per hour.",
        "compliance": "I'll look up mapped CIS / NIST / ISO controls for the findings in scope.",
        "impact": "I'll estimate breach cost and compliance deltas using current scoring outputs.",
        "summary": "I'll assemble an executive-ready HTML summary including top priorities and controls.",
        "general": "I can optimize plans, map controls, narrate findings, or draft summaries on request.",
    }

    return NLQueryResponse(intent=intent, response=responses[intent], details={"confidence": round(confidence, 2)})
