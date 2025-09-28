from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, MutableMapping

from .config_loader import scoring_config

ScoreFinding = Dict[str, Any]
ScoreResponse = Dict[str, Any]


def _context_multiplier(finding: Mapping[str, Any], cfg: Mapping[str, Any]) -> float:
    modifiers = cfg.get("context_modifiers", {})
    multiplier = 1.0
    asset = finding.get("asset") or {}
    if not isinstance(asset, Mapping):
        return multiplier

    for key, default in (
        ("criticality", 1.0),
        ("exposure", 1.0),
        ("data_sensitivity", 1.0),
    ):
        value = asset.get(key)
        if value is None:
            continue
        options = modifiers.get(key, {})
        multiplier *= float(options.get(value, default))
    return multiplier


def _priority_for_score(score: float, buckets: Iterable[Mapping[str, Any]]) -> str:
    for bucket in sorted(buckets, key=lambda item: float(item.get("min", 0.0)), reverse=True):
        if score >= float(bucket.get("min", 0.0)):
            return str(bucket.get("name", "Unclassified"))
    return "Unclassified"


def _coerce_hours(value: Any) -> float:
    try:
        return max(float(value), 0.0)
    except (TypeError, ValueError):
        return 0.0


def score_compute(findings: Iterable[Mapping[str, Any]], cfg: Mapping[str, Any] | None = None) -> ScoreResponse:
    """Compute weighted risk scores for a collection of findings.

    Each finding is scored using weighted components for CVSS, EPSS, MVI,
    Known Exploited Vulnerabilities (KEV) boosts, and business context
    multipliers. Scores are clipped between 0 and 10. Effort hours are
    carried into the response alongside aggregate totals for quick
    downstream consumption by optimizers or summaries.
    """

    config = cfg or scoring_config()
    weights: MutableMapping[str, float] = {
        key: float(value)
        for key, value in config.get("weights", {}).items()
    }
    buckets = config.get("priority_buckets", [])

    scored_findings: List[ScoreFinding] = []
    totals: Dict[str, Any] = {
        "count": 0,
        "total_score": 0.0,
        "total_effort_hours": 0.0,
        "by_priority": {},
    }

    for finding in findings:
        totals["count"] += 1

        cvss = float(finding.get("cvss", 0.0))
        epss = float(finding.get("epss", 0.0) or 0.0)
        mvi = float(finding.get("mvi", 0.0) or 0.0)
        kev = bool(finding.get("kev"))
        effort_hours = _coerce_hours(finding.get("effort_hours"))

        cvss_component = cvss * weights.get("cvss", 0.0)
        epss_component = epss * 10.0 * weights.get("epss", 0.0)
        mvi_component = mvi * weights.get("mvi", 0.0)
        kev_component = (10.0 if kev else 0.0) * weights.get("kev", 0.0)

        base_score = cvss_component + epss_component + mvi_component + kev_component

        multiplier = _context_multiplier(finding, config)
        context_weight = weights.get("context", 0.0)
        context_component = base_score * (multiplier - 1.0) * context_weight

        raw_score = base_score + context_component
        score = max(0.0, min(round(raw_score, 2), 10.0))

        priority = _priority_for_score(score, buckets)
        totals["by_priority"][priority] = totals["by_priority"].get(priority, 0) + 1
        totals["total_score"] += score
        totals["total_effort_hours"] += effort_hours

        scored_findings.append(
            {
                "id": finding.get("id"),
                "title": finding.get("title"),
                "score": score,
                "priority": priority,
                "effort_hours": effort_hours,
                "components": {
                    "cvss": round(cvss_component, 2),
                    "epss": round(epss_component, 2),
                    "mvi": round(mvi_component, 2),
                    "kev": round(kev_component, 2),
                    "context": round(context_component, 2),
                },
                "context_multiplier": round(multiplier, 2),
            }
        )

    average_score = (
        totals["total_score"] / totals["count"] if totals["count"] else 0.0
    )
    totals["average_score"] = round(average_score, 2)
    totals["total_score"] = round(totals["total_score"], 2)
    totals["total_effort_hours"] = round(totals["total_effort_hours"], 2)

    return {"findings": scored_findings, "totals": totals}
