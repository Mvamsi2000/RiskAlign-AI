from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .impact import impact_estimate
from .mapping import map_to_controls
from .optimizer import optimize_plan
from .scoring import score_compute

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

_template_env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates")),
    autoescape=select_autoescape(["html", "xml"]),
)


def _load_sample_findings() -> List[Dict[str, Any]]:
    sample_path = BASE_DIR / "data" / "sample_findings.json"
    if sample_path.exists():
        return json.loads(sample_path.read_text(encoding="utf-8"))
    return []


def _ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_summary(
    findings: Iterable[Mapping[str, Any]] | None = None,
    *,
    scope: str = "environment",
    framework: str = "CIS",
    max_hours_per_wave: float = 16.0,
) -> Dict[str, Any]:
    findings_list = list(findings or _load_sample_findings())

    scoring = score_compute(findings_list)
    plan = optimize_plan(
        findings_list,
        max_hours_per_wave=max_hours_per_wave,
        scored=scoring["findings"],
    )
    impact = impact_estimate(plan["waves"], findings_list)
    controls = map_to_controls(findings_list, framework=framework)

    rendered_at = datetime.now(UTC)
    template = _template_env.get_template("summary.html")
    html = template.render(
        scope=scope,
        generated_at=rendered_at.strftime("%Y-%m-%d %H:%M UTC"),
        scoring=scoring,
        plan=plan,
        impact=impact,
        controls=controls,
    )

    _ensure_output_dir()
    filename = OUTPUT_DIR / f"summary-{rendered_at.strftime('%Y%m%d%H%M%S')}.html"
    filename.write_text(html, encoding="utf-8")

    return {"path": str(filename), "html": html}
