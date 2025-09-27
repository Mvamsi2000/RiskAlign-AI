from __future__ import annotations

from typing import List

from .config_loader import controls_mapping
from .schemas import ControlMapping, MapControlsRequest, MapControlsResponse


def map_to_controls(request: MapControlsRequest) -> MapControlsResponse:
    mapping = controls_mapping()
    results: List[ControlMapping] = []
    for cve in request.cves:
        controls = mapping.get(cve, [])
        for control in controls:
            results.append(
                ControlMapping(
                    control=control["control"],
                    description=control.get("description", ""),
                    finding=cve,
                )
            )
    return MapControlsResponse(mappings=results)
