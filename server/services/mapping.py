"""Placeholder mapping service returning deterministic coverage rows."""
from __future__ import annotations

from server import config_loader
from server.schemas.api import MappingRequest, MappingResponse, MappingRow


def map_to_controls(payload: MappingRequest) -> MappingResponse:
    """Return a stubbed set of control mappings for the provided findings."""
    framework = payload.framework.upper()
    config = config_loader.controls_mapping()
    controls = config.get(framework, {})

    rows = [
        MappingRow(
            control_id=control_id,
            title=entry.get("name", control_id),
            description=entry.get("description", ""),
            related_findings=[finding.id for finding in payload.findings],
        )
        for control_id, entry in controls.items()
    ]

    coverage = 100.0 if rows else 0.0
    return MappingResponse(framework=framework, coverage_pct=coverage, rows=rows)
