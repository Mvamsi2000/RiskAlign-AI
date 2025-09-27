from __future__ import annotations

from typing import Dict, Iterable, List

from ..schemas import Finding, ScoreComputeResponse, ScoreContribution, ScoredFinding


def _priority_from_score(score: float, buckets: Dict[str, float]) -> str:
    if score >= buckets.get("critical", 9):
        return "critical"
    if score >= buckets.get("high", 7):
        return "high"
    if score >= buckets.get("medium", 4):
        return "medium"
    return "low"


def compute_scores(findings: Iterable[Finding], config: Dict) -> ScoreComputeResponse:
    weights = config.get("weights", {})
    buckets = config.get("priority_buckets", {})
    recommendations = config.get("recommended_actions", {})

    scored: List[ScoredFinding] = []
    for finding in findings:
        contributions: List[ScoreContribution] = []
        score = 0.0

        cvss_weight = weights.get("cvss", 0)
        cvss_score = finding.cvss * cvss_weight
        contributions.append(
            ScoreContribution(
                signal="CVSS base score",
                weight=cvss_weight,
                value=finding.cvss,
                impact=cvss_score,
                rationale="Severity baseline from CVSS multiplied by configured weight.",
            )
        )
        score += cvss_score

        epss_weight = weights.get("epss", 0)
        epss_value = finding.epss * 10
        epss_score = epss_value * epss_weight
        contributions.append(
            ScoreContribution(
                signal="EPSS likelihood",
                weight=epss_weight,
                value=round(epss_value, 2),
                impact=epss_score,
                rationale="Exploit probability scaled to CVSS range.",
            )
        )
        score += epss_score

        kev_weight = weights.get("kev", 0)
        kev_value = 10 if finding.kev else 0
        kev_score = kev_value * kev_weight
        contributions.append(
            ScoreContribution(
                signal="Known exploited vulnerability",
                weight=kev_weight,
                value=kev_value,
                impact=kev_score,
                rationale="Boost for vulnerabilities on CISA KEV list.",
            )
        )
        score += kev_score

        criticality_weight = weights.get("asset_criticality", 0)
        criticality_value = (finding.asset_criticality / 5) * 10
        criticality_score = criticality_value * criticality_weight
        contributions.append(
            ScoreContribution(
                signal="Asset criticality",
                weight=criticality_weight,
                value=round(criticality_value, 2),
                impact=criticality_score,
                rationale="Higher criticality assets increase the business risk.",
            )
        )
        score += criticality_score

        exposure_signal = f"exposure_{finding.exposure.value}"
        exposure_weight = weights.get(exposure_signal, 0)
        exposure_value = 10 if finding.exposure.value == "external" else 6 if finding.exposure.value == "partial" else 3
        exposure_score = exposure_value * exposure_weight
        contributions.append(
            ScoreContribution(
                signal=f"Exposure: {finding.exposure.value}",
                weight=exposure_weight,
                value=exposure_value,
                impact=exposure_score,
                rationale="External exposure attracts a higher multiplier than internal-only findings.",
            )
        )
        score += exposure_score

        sensitivity_signal = f"data_{finding.data_sensitivity.value}"
        sensitivity_weight = weights.get(sensitivity_signal, 0)
        sensitivity_value = {
            "public": 2,
            "internal": 4,
            "confidential": 7,
            "high": 9,
        }.get(finding.data_sensitivity.value, 4)
        sensitivity_score = sensitivity_value * sensitivity_weight
        contributions.append(
            ScoreContribution(
                signal=f"Data sensitivity: {finding.data_sensitivity.value}",
                weight=sensitivity_weight,
                value=sensitivity_value,
                impact=sensitivity_score,
                rationale="Handling sensitive data increases downstream impact of breaches.",
            )
        )
        score += sensitivity_score

        effort_weight = weights.get("effort_modifier", 0)
        effort_score = finding.effort_hours * effort_weight
        contributions.append(
            ScoreContribution(
                signal="Remediation effort",
                weight=effort_weight,
                value=finding.effort_hours,
                impact=effort_score,
                rationale="Higher effort slightly reduces prioritization to surface quick wins.",
            )
        )
        score += effort_score

        priority = _priority_from_score(score, buckets)
        recommendation = recommendations.get(
            priority,
            "Log finding for review and include in remediation backlog.",
        )

        scored.append(
            ScoredFinding(
                finding=finding,
                score=round(score, 2),
                priority=priority,
                contributions=contributions,
                recommended_action=recommendation,
            )
        )

    return ScoreComputeResponse(findings=scored)
