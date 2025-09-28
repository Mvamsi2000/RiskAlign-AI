from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence, Set

from .config_loader import controls_mapping

ImpactResponse = Dict[str, Any]


def _collect_controls(ids: Sequence[str | None], findings: Iterable[Mapping[str, Any]]) -> Set[str]:
    id_to_cve = {}
    for finding in findings:
        identifier = finding.get("id")
        if identifier is None:
            continue
        id_to_cve[identifier] = finding.get("cve")

    mapping = controls_mapping()
    covered: Set[str] = set()
    for identifier in ids:
        if not identifier:
            continue
        cve = id_to_cve.get(identifier)
        if not cve:
            continue
        for control in mapping.get(cve, []):
            covered.add(control["control"])
    return covered


def impact_estimate(
    waves: Iterable[Mapping[str, Any]],
    findings: Iterable[Mapping[str, Any]] | None = None,
) -> ImpactResponse:
    """Estimate program impact from remediation waves."""

    wave_list = [dict(wave) for wave in waves]
    finding_list = list(findings or [])

    total_risk = sum(float(wave.get("risk_saved", 0.0)) for wave in wave_list)
    total_risk = round(total_risk, 2)

    cumulative = 0.0
    curve: List[Dict[str, Any]] = []
    for wave in wave_list:
        risk = float(wave.get("risk_saved", 0.0))
        cumulative += risk
        percent = (cumulative / total_risk * 100.0) if total_risk else 0.0
        curve.append(
            {
                "wave": str(wave.get("name", "")),
                "cumulative_risk_saved": round(cumulative, 2),
                "percent_of_total": round(percent, 2),
            }
        )

    item_count = sum(len(wave.get("items", [])) for wave in wave_list)
    denominator = max(item_count, len(finding_list), 1)
    max_possible_risk = denominator * 12.5  # score 10 with critical boost
    readiness = min(total_risk / max_possible_risk * 100.0, 100.0)

    covered_controls: Set[str] = set()
    if finding_list:
        ids = [item.get("id") for wave in wave_list for item in wave.get("items", [])]
        covered_controls = _collect_controls(ids, finding_list)

    compliance = min(len(covered_controls) * 6.0 + total_risk * 0.4, 100.0)

    return {
        "readiness_percent": round(readiness, 2),
        "risk_saved_curve": curve,
        "compliance_boost": round(compliance, 2),
        "controls_covered": sorted(covered_controls),
    }
