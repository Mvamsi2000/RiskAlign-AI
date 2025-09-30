"""Placeholder scoring service until the analytics engine is implemented."""
from __future__ import annotations

from typing import Iterable

from server.schemas.api import ScoreFinding, ScoreRequest, ScoreResponse, ScoreSummary

DEFAULT_SCORE = 5.0
DEFAULT_BUCKET = "medium"
DEFAULT_EFFORT = 4.0


def score_compute(payload: ScoreRequest) -> ScoreResponse:
    """Return a deterministic scoring response for the supplied findings."""
    scored: Iterable[ScoreFinding] = (
        ScoreFinding(
            **finding.model_dump(),
            score=DEFAULT_SCORE,
            bucket=DEFAULT_BUCKET,
            effort_hours=DEFAULT_EFFORT,
        )
        for finding in payload.findings
    )
    scored_list = list(scored)

    summary = ScoreSummary(
        total_findings=len(scored_list),
        average_score=DEFAULT_SCORE if scored_list else 0.0,
        critical=0,
        high=0,
        medium=len(scored_list),
        low=0,
        total_effort_hours=DEFAULT_EFFORT * len(scored_list),
    )

    return ScoreResponse(findings=scored_list, summary=summary)
