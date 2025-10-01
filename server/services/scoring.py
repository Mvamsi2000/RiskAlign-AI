"""Risk scoring service combining CVSS, EPSS, KEV and contextual signals."""
from __future__ import annotations

from collections import Counter
from typing import Iterable, Tuple

from server import config_loader
from server.schemas import (
    CanonicalFinding,
    ScoreComputeResponse,
    ScoreComponents,
    ScoreFinding,
    ScoreRequest,
    ScoreTotals,
    ScoringConfig,
)

_SEVERITY_DEFAULTS = {
    "critical": 9.5,
    "high": 8.0,
    "medium": 5.5,
    "low": 3.0,
}

_PRIORITY_THRESHOLDS: Tuple[Tuple[float, str], ...] = (
    (9.0, "Critical"),
    (7.0, "High"),
    (4.0, "Medium"),
    (0.0, "Low"),
)

_CONTEXT_BONUS = {
    "criticality": {"critical": 0.2, "high": 0.15, "medium": 0.05},
    "exposure": {"internet": 0.1, "dmz": 0.08, "internal": 0.03},
}


def _load_config(override: ScoringConfig | None) -> ScoringConfig:
    if override:
        return override
    raw = config_loader.scoring_config()
    return ScoringConfig(**raw)


def _base_cvss(finding: CanonicalFinding) -> float:
    if finding.cvss is not None:
        return float(finding.cvss)
    if finding.severity:
        return _SEVERITY_DEFAULTS.get(finding.severity.lower(), 5.0)
    return 5.0


def _context_multiplier(finding: CanonicalFinding) -> float:
    multiplier = 1.0
    asset = finding.asset
    if asset:
        if asset.criticality:
            bonus = _CONTEXT_BONUS["criticality"].get(asset.criticality.lower(), 0.0)
            multiplier += bonus
        if asset.exposure:
            bonus = _CONTEXT_BONUS["exposure"].get(asset.exposure.lower(), 0.0)
            multiplier += bonus
        if asset.data_sensitivity:
            multiplier += 0.05
    if "kev" in (finding.tags or []):
        multiplier += 0.05
    return min(multiplier, 1.6)


def _priority(score: float) -> str:
    for threshold, label in _PRIORITY_THRESHOLDS:
        if score >= threshold:
            return label
    return "Low"


def _estimate_effort(finding: CanonicalFinding, base_cvss: float) -> float:
    if finding.effort_hours is not None:
        return float(finding.effort_hours)
    if base_cvss >= 9:
        effort = 16.0
    elif base_cvss >= 7:
        effort = 10.0
    elif base_cvss >= 4:
        effort = 6.0
    else:
        effort = 3.0
    asset = finding.asset
    if asset:
        if asset.criticality and asset.criticality.lower() == "high":
            effort += 2.0
        if asset.exposure and asset.exposure.lower() == "internet":
            effort += 1.0
    if "misconfiguration" in (finding.tags or []):
        effort -= 1.0
    return max(2.0, effort)


def _components(finding: CanonicalFinding, config: ScoringConfig) -> Tuple[ScoreComponents, float, float, float, float]:
    weights = config.weights
    base_cvss = _base_cvss(finding)
    epss = float(finding.epss or 0.05)
    mvi = float(finding.mvi or 0.3)
    kev_flag = 1.0 if finding.kev else 0.0

    context_multiplier = _context_multiplier(finding)

    cvss_component = base_cvss * weights.cvss
    epss_component = epss * 10 * weights.epss
    mvi_component = mvi * 10 * 0.05
    kev_component = kev_flag * 10 * weights.kev
    context_component = max(context_multiplier - 1.0, 0) * config.max_score * weights.context

    total = (cvss_component + epss_component + mvi_component + kev_component)
    adjusted = min(config.max_score, total * context_multiplier + context_component)

    components = ScoreComponents(
        cvss=cvss_component,
        epss=epss_component,
        mvi=mvi_component,
        kev=kev_component,
        context=context_component,
    )

    effort = _estimate_effort(finding, base_cvss)
    risk_saved = max(adjusted - config.risk_tolerance, 0.0) * 1.2

    return components, adjusted, context_multiplier, risk_saved, effort


def score_compute(payload: ScoreRequest) -> ScoreComputeResponse:
    """Calculate risk scores for the supplied findings."""

    config = _load_config(payload.config)
    scored_findings: list[ScoreFinding] = []

    for finding in payload.findings:
        components, score, context_multiplier, risk_saved, effort = _components(finding, config)
        priority = _priority(score)

        scored_findings.append(
            ScoreFinding(
                **finding.model_dump(mode="json", exclude_none=True),
                score=round(score, 2),
                priority=priority,
                effort_hours=round(effort, 2),
                risk_saved=round(risk_saved, 2),
                components=components,
                context_multiplier=round(context_multiplier, 2),
            )
        )

    totals = _summarize(scored_findings)
    return ScoreComputeResponse(findings=scored_findings, totals=totals)


def _summarize(findings: Iterable[ScoreFinding]) -> ScoreTotals:
    findings_list = list(findings)
    count = len(findings_list)
    total_score = sum(item.score for item in findings_list)
    total_effort = sum(item.effort_hours for item in findings_list)
    by_priority = Counter(item.priority for item in findings_list)
    average = total_score / count if count else 0.0

    return ScoreTotals(
        count=count,
        total_score=round(total_score, 2),
        average_score=round(average, 2),
        total_effort_hours=round(total_effort, 2),
        by_priority=dict(by_priority),
    )


__all__ = ["score_compute"]
