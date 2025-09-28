from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Set

from .config_loader import controls_mapping

MappingResponse = Dict[str, Any]


def map_to_controls(
    findings: Iterable[Mapping[str, Any]],
    framework: str = "CIS",
) -> MappingResponse:
    framework_key = framework.upper()
    if framework_key != "CIS":
        raise ValueError(f"Unsupported framework '{framework}'. Only CIS is available in the MVP.")

    mapping = controls_mapping()

    mappings: List[Dict[str, Any]] = []
    unique_controls: Set[str] = set()
    covered_cves: Set[str] = set()
    total_cves = 0
    missing: List[str] = []

    for finding in findings:
        cve = finding.get("cve")
        if not cve:
            continue
        total_cves += 1
        controls = mapping.get(cve, [])
        if not controls:
            missing.append(cve)
            continue
        covered_cves.add(cve)
        for control in controls:
            unique_controls.add(control["control"])
            mappings.append(
                {
                    "cve": cve,
                    "control": control["control"],
                    "description": control.get("description", ""),
                    "finding_id": finding.get("id"),
                }
            )

    coverage = (len(covered_cves) / total_cves * 100.0) if total_cves else 0.0

    return {
        "framework": framework_key,
        "coverage": round(coverage, 2),
        "unique_controls": sorted(unique_controls),
        "mappings": mappings,
        "unmapped": sorted(set(missing)),
    }
