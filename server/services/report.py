"""HTML report rendering service."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from server.schemas import (
    ImpactEstimateResponse,
    ImpactRequest,
    MappingRequest,
    MappingResponse,
    PlanTotals,
    ScoreFinding,
    SummaryGenerateResponse,
    SummaryRequest,
)

from .impact import estimate_impact
from .mapping import map_to_controls

_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
_ENV = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"]),
    enable_async=False,
)


def _ensure_assets() -> None:
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stylesheet = _TEMPLATE_DIR / "base.css"
    if stylesheet.exists():
        target = _OUTPUT_DIR / "base.css"
        if not target.exists():
            target.write_text(stylesheet.read_text(encoding="utf-8"), encoding="utf-8")


def _summaries(findings: list[ScoreFinding]) -> Dict[str, object]:
    total = len(findings)
    total_score = sum(item.score for item in findings)
    average = total_score / total if total else 0.0
    total_effort = sum(item.effort_hours for item in findings)
    top_risks = sorted(findings, key=lambda item: item.score, reverse=True)[:5]
    priority_counts: Dict[str, int] = {}
    for item in findings:
        priority_counts[item.priority] = priority_counts.get(item.priority, 0) + 1
    return {
        "count": total,
        "total_score": round(total_score, 2),
        "average_score": round(average, 2),
        "total_effort": round(total_effort, 2),
        "priority_counts": priority_counts,
        "top_risks": top_risks,
    }


def _plan_totals(waves: list) -> PlanTotals:
    return PlanTotals(
        waves=len(waves),
        total_hours=round(sum(w.total_hours for w in waves), 2),
        total_risk_saved=round(sum(w.risk_saved for w in waves), 2),
    )


def generate_summary(payload: SummaryRequest) -> SummaryGenerateResponse:
    """Render the executive summary template with the supplied analytics."""

    _ensure_assets()

    findings = list(payload.findings)
    waves = list(payload.waves)

    impact: ImpactEstimateResponse
    if payload.impact:
        impact = payload.impact
    else:
        impact = estimate_impact(
            ImpactRequest(findings=findings, waves=waves, framework="CIS")
        )

    mapping: MappingResponse
    if payload.mapping:
        mapping = payload.mapping
    else:
        mapping = map_to_controls(MappingRequest(findings=findings, framework="CIS"))

    template = _ENV.get_template("executive_summary.html")
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    context = {
        "generated_at": generated_at,
        "notes": payload.notes,
        "findings": findings,
        "waves": waves,
        "impact": impact,
        "mapping": mapping,
        "score_summary": _summaries(findings),
        "plan_totals": _plan_totals(waves),
    }

    html = template.render(**context)

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"executive-summary-{timestamp}.html"
    report_path = _OUTPUT_DIR / filename
    report_path.write_text(html, encoding="utf-8")

    return SummaryGenerateResponse(path=f"/reports/{filename}", html=html)


__all__ = ["generate_summary"]
