from __future__ import annotations

from typing import Any, Dict, List, Mapping

_INTENTS: List[Dict[str, Any]] = [
    {
        "name": "score",
        "keywords": ["score", "priorit", "risk", "ranking"],
        "endpoint": "/api/score/compute",
        "message": "I can compute weighted risk scores with context and effort totals.",
    },
    {
        "name": "plan",
        "keywords": ["plan", "wave", "schedule", "optimize", "remediation"],
        "endpoint": "/api/optimize/plan",
        "message": "I'll build remediation waves based on risk saved per hour.",
    },
    {
        "name": "map",
        "keywords": ["map", "control", "compliance", "cis", "coverage"],
        "endpoint": "/api/map/controls",
        "message": "I'll map the CVEs to CIS controls and highlight coverage gaps.",
    },
    {
        "name": "summary",
        "keywords": ["summary", "report", "executive", "narrative", "html"],
        "endpoint": "/api/summary/generate",
        "message": "I'll render the printable summary with scores, plan, and controls.",
    },
]

_DEFAULT_RESPONSE = {
    "intent": "help",
    "response": "I can help you score findings, plan remediation waves, map controls, or generate summaries.",
    "details": {"matched_keywords": [], "confidence": 0.0, "endpoint": None},
}


def nl_query(payload: Mapping[str, Any]) -> Dict[str, Any]:
    query = str(payload.get("query", "")).lower()
    if not query.strip():
        return _DEFAULT_RESPONSE

    best = {"intent": "help", "confidence": 0.0, "matched": []}

    for entry in _INTENTS:
        matched = [kw for kw in entry["keywords"] if kw in query]
        if not matched:
            continue
        confidence = len(matched) / len(entry["keywords"])
        if confidence > best["confidence"]:
            best = {"intent": entry["name"], "confidence": confidence, "matched": matched, "endpoint": entry["endpoint"], "message": entry["message"]}

    if best["confidence"] == 0.0:
        return _DEFAULT_RESPONSE

    return {
        "intent": best["intent"],
        "response": best["message"],
        "details": {
            "matched_keywords": best["matched"],
            "confidence": round(best["confidence"], 2),
            "endpoint": best["endpoint"],
        },
    }
