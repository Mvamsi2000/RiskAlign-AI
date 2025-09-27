from __future__ import annotations

from typing import Dict, List

from ..schemas import ComplianceMappingResponse, ControlMapping


def map_to_controls(cves: List[str], mapping: Dict[str, List[Dict[str, str]]]) -> ComplianceMappingResponse:
    normalized = {key.upper(): value for key, value in mapping.items()}
    response: Dict[str, List[ControlMapping]] = {}

    for cve in cves:
        controls = [
            ControlMapping(**control)
            for control in normalized.get(cve.upper(), [])
        ]
        response[cve] = controls

    return ComplianceMappingResponse(mappings=response)
