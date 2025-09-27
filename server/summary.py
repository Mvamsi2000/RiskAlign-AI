from __future__ import annotations

import json
from pathlib import Path
from typing import List

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .mapping import map_to_controls
from .scoring import compute_scores
from .schemas import (
    ControlMapping,
    Finding,
    MapControlsRequest,
    SummaryGenerateRequest,
    SummaryGenerateResponse,
)

BASE_DIR = Path(__file__).resolve().parent

_TEMPLATE_ENV = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates")),
    autoescape=select_autoescape(["html", "xml"]),
)


def generate_summary(request: SummaryGenerateRequest) -> SummaryGenerateResponse:
    findings: List[Finding]
    if request.findings:
        findings = request.findings
    else:
        sample_path = BASE_DIR / "data" / "sample_findings.json"
        if sample_path.exists():
            raw = json.loads(sample_path.read_text(encoding="utf-8"))
            findings = [Finding.model_validate(item) for item in raw]
        else:
            findings = []

    scores = compute_scores(findings)
    top_findings = sorted(scores.results, key=lambda item: item.score, reverse=True)[:3]

    cves = [finding.cve for finding in findings if finding.cve]
    controls: List[ControlMapping] = []
    if cves:
        controls = map_to_controls(MapControlsRequest(cves=cves)).mappings
    else:
        controls = []

    impact = {
        "breach_reduction": min(sum(item.score for item in top_findings) * 1.2, 100.0),
        "compliance_gain": min(len(controls) * 5.0, 100.0),
    }

    template = _TEMPLATE_ENV.get_template("executive_summary.html")
    html = template.render(
        narrative=(
            "RiskAlign-AI highlights top priorities with contextual business impact, "
            f"focusing on the {request.scope or 'environment'} scope."
        ),
        top_findings=top_findings,
        impact=impact,
        controls=controls,
    )

    return SummaryGenerateResponse(html=html)
