"""Placeholder report generation service."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from server.schemas.api import SummaryRequest, SummaryResponse

_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def _ensure_stylesheet() -> None:
    stylesheet = _TEMPLATE_DIR / "base.css"
    target = _OUTPUT_DIR / "base.css"
    if stylesheet.exists() and not target.exists():
        target.write_text(stylesheet.read_text(encoding="utf-8"), encoding="utf-8")


def generate_summary(payload: SummaryRequest) -> SummaryResponse:
    """Render a lightweight HTML report stub and return its relative URL."""
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _ensure_stylesheet()

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"summary-{timestamp}.html"
    report_path = _OUTPUT_DIR / filename

    findings_count = len(payload.findings)
    waves_count = len(payload.waves)

    report_path.write_text(
        "\n".join(
            [
                "<!DOCTYPE html>",
                "<html lang=\"en\">",
                "<head>",
                "  <meta charset=\"utf-8\">",
                "  <title>RiskAlign Summary (Placeholder)</title>",
                "  <link rel=\"stylesheet\" href=\"/reports/base.css\">",
                "</head>",
                "<body>",
                "  <main>",
                "    <h1>RiskAlign Executive Summary (Stub)",
                "    </h1>",
                f"    <p>Total findings: {findings_count}</p>",
                f"    <p>Total waves: {waves_count}</p>",
                "    <p>The detailed narrative report will be implemented in a later milestone.</p>",
                "  </main>",
                "</body>",
                "</html>",
            ]
        ),
        encoding="utf-8",
    )

    return SummaryResponse(report_url=f"/reports/{filename}")
