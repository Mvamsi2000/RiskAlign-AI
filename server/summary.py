from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

from fastapi import Request
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .ai.usecases import generate_summary_narrative
from .impact import impact_estimate
from .mapping import map_to_controls
from .optimizer import optimize_plan
from .scoring import score_compute
from .core.tenancy import get_namespace, output_path
from .ingest.pipeline import load_latest_canonical

BASE_DIR = Path(__file__).resolve().parent

_template_env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates")),
    autoescape=select_autoescape(["html", "xml"]),
)


def _load_sample_findings() -> List[Dict[str, Any]]:
    sample_path = BASE_DIR / "data" / "sample_findings.json"
    if sample_path.exists():
        return json.loads(sample_path.read_text(encoding="utf-8"))
    return []


def _load_namespace_findings(namespace: Optional[str]) -> List[Dict[str, Any]]:
    if namespace:
        canonical, _ = load_latest_canonical(namespace)
        if canonical:
            return canonical
    return _load_sample_findings()


def generate_summary(
    findings: Iterable[Mapping[str, Any]] | None = None,
    *,
    scope: str = "environment",
    framework: str = "CIS",
    max_hours_per_wave: float = 16.0,
    request: Optional[Request] = None,
    tenant_config: Optional[Mapping[str, Any]] = None,
    namespace: Optional[str] = None,
) -> Dict[str, Any]:
    namespace = namespace or get_namespace(request)
    findings_list = list(findings or _load_namespace_findings(namespace))

    scoring = score_compute(findings_list)
    plan = optimize_plan(
        findings_list,
        max_hours_per_wave=max_hours_per_wave,
        scored=scoring["findings"],
    )
    impact = impact_estimate(plan["waves"], findings_list)
    controls = map_to_controls(findings_list, framework=framework)

    rendered_at = datetime.now(UTC)
    namespace = namespace or get_namespace(request)

    ai_context = {
        "scope": scope,
        "totals": scoring.get("totals", {}),
        "waves": plan.get("waves", []),
        "impact": impact,
        "controls": {
            "framework": controls.get("framework"),
            "coverage": controls.get("coverage"),
            "unmapped": controls.get("unmapped"),
        },
    }
    ai_narrative = generate_summary_narrative(
        request,
        tenant_config=tenant_config,
        namespace=namespace,
        context=ai_context,
    )

    template = _template_env.get_template("summary.html")
    html = template.render(
        scope=scope,
        generated_at=rendered_at.strftime("%Y-%m-%d %H:%M UTC"),
        scoring=scoring,
        plan=plan,
        impact=impact,
        controls=controls,
        ai_narrative=ai_narrative,
    )

    output_dir = output_path(namespace)
    filename = output_dir / f"summary-{rendered_at.strftime('%Y%m%d%H%M%S')}.html"
    filename.write_text(html, encoding="utf-8")

    return {"path": str(filename), "html": html}
