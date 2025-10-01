"""Map findings to CIS controls using simple heuristics."""
from __future__ import annotations

from typing import Dict, Iterable, List, Set

from server import config_loader
from server.schemas import ControlMapping, MappingRequest, MappingResponse


def _load_controls(framework: str) -> Dict[str, Dict[str, object]]:
    data = config_loader.controls_mapping()
    return data.get(framework.upper(), {})


def _matches_control(text: str, keywords: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def map_to_controls(payload: MappingRequest) -> MappingResponse:
    """Map normalized findings to CIS controls."""

    controls = _load_controls(payload.framework)
    if not controls:
        return MappingResponse(framework=payload.framework.upper(), coverage=0.0)

    mappings: List[ControlMapping] = []
    matched_controls: Set[str] = set()
    unmapped: List[str] = []

    for finding in payload.findings:
        matched = False
        text = " ".join(
            filter(
                None,
                [finding.title, finding.description, " ".join(finding.tags or []), finding.remediation or ""],
            )
        )
        for control_id, entry in controls.items():
            keywords = entry.get("keywords", [])
            cves = entry.get("cves", [])
            has_keyword = _matches_control(text, keywords) if keywords else False
            has_cve = finding.cve in cves if finding.cve else False
            if has_keyword or has_cve:
                matched = True
                matched_controls.add(control_id)
                mappings.append(
                    ControlMapping(
                        control=control_id,
                        title=str(entry.get("name", control_id)),
                        description=str(entry.get("description", "")),
                        finding_id=finding.id,
                        cve=finding.cve,
                    )
                )
        if not matched:
            unmapped.append(finding.id)

    coverage = (len(matched_controls) / len(controls)) * 100 if controls else 0.0

    return MappingResponse(
        framework=payload.framework.upper(),
        coverage=round(coverage, 2),
        unique_controls=sorted(matched_controls),
        mappings=mappings,
        unmapped=unmapped,
    )


__all__ = ["map_to_controls"]
