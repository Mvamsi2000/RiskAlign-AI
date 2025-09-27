from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List

from .config_loader import scoring_config
from .schemas import Contribution, Finding, ScoreComputeResponse, ScoreSummary, ScoredFinding


def _context_multiplier(finding: Finding, config: Dict) -> float:
    modifiers = config.get("context_modifiers", {})
    multiplier = 1.0
    asset = finding.asset
    if not asset:
        return multiplier

    for field in ("criticality", "exposure", "data_sensitivity"):
        value = getattr(asset, field, None)
        if not value:
            continue
        options = modifiers.get(field, {})
        multiplier *= options.get(value, 1.0)
    return multiplier


def _priority_for_score(score: float, buckets: Iterable[Dict]) -> str:
    for bucket in sorted(buckets, key=lambda item: item["min"], reverse=True):
        if score >= bucket["min"]:
            return bucket["name"]
    return "Unclassified"


def compute_scores(findings: List[Finding]) -> ScoreComputeResponse:
    config = scoring_config()
    weights = config.get("weights", {})
    buckets = config.get("priority_buckets", [])

    results: List[ScoredFinding] = []
    priority_counts: Dict[str, int] = {}

    for finding in findings:
        multiplier = _context_multiplier(finding, config)
        cvss_component = finding.cvss * weights.get("cvss", 0)
        epss = finding.epss or 0.0
        epss_component = epss * 10 * weights.get("epss", 0)
        kev_component = (10.0 if finding.kev else 0.0) * weights.get("kev", 0)
        context_component = (multiplier - 1.0) * 10 * weights.get("context", 0)

        raw_score = cvss_component + epss_component + kev_component
        adjusted_score = min(raw_score * multiplier + context_component, 10.0)
        score = round(adjusted_score, 2)

        priority = _priority_for_score(score, buckets)
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

        contributions = [
            Contribution(
                name="CVSS base",
                weight=weights.get("cvss", 0.0),
                value=finding.cvss,
                contribution=round(cvss_component, 2),
                description="Base severity provided by CVSS",
            ),
            Contribution(
                name="EPSS likelihood",
                weight=weights.get("epss", 0.0),
                value=epss,
                contribution=round(epss_component, 2),
                description="Exploit probability (EPSS scaled to 10)",
            ),
            Contribution(
                name="Known exploited",
                weight=weights.get("kev", 0.0),
                value=1.0 if finding.kev else 0.0,
                contribution=round(kev_component, 2),
                description="Boost applied when vulnerability is on the KEV list",
            ),
            Contribution(
                name="Context multiplier",
                weight=weights.get("context", 0.0),
                value=round(multiplier, 2),
                contribution=round(context_component, 2),
                description="Business context adjustments based on asset metadata",
            ),
        ]

        narrative = (
            f"{finding.title} scores {score} ({priority}). "
            f"Asset '{finding.asset.name if finding.asset else 'unknown'}' with {finding.asset.criticality if finding.asset else 'n/a'} "
            "criticality and exposure to "
            f"{finding.asset.exposure if finding.asset else 'n/a'} keeps this finding in focus."
        )

        rules_applied = [
            "Weighted sum of CVSS, EPSS, KEV, and context multipliers",
            f"Context multiplier set to {multiplier:.2f}",
            f"Priority bucket: {priority}",
        ]

        results.append(
            ScoredFinding(
                id=finding.id,
                title=finding.title,
                score=score,
                priority=priority,
                contributions=contributions,
                narrative=narrative,
                rules_applied=rules_applied,
            )
        )

    summary = ScoreSummary(counts_by_priority=priority_counts, generated_at=datetime.utcnow())
    return ScoreComputeResponse(results=results, summary=summary)
