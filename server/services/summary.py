from __future__ import annotations

from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..schemas import Finding, SummaryGenerateResponse
from .scoring import compute_scores

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_summary(scope: str, findings: Iterable[Finding], config: Dict) -> SummaryGenerateResponse:
    scoring = compute_scores(findings, config)
    scores = [item.score for item in scoring.findings]
    priorities = Counter(item.priority for item in scoring.findings)
    total_hours = sum(item.finding.effort_hours for item in scoring.findings)
    avg_score = mean(scores) if scores else 0.0

    template = _env.get_template("executive_summary.html")
    html = template.render(
        scope=scope,
        avg_score=round(avg_score, 2),
        priorities=priorities,
        total_hours=round(total_hours, 1),
        findings=scoring.findings,
    )
    return SummaryGenerateResponse(html=html)
