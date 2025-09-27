"""FastAPI application entry point for RiskAlign-AI."""

from fastapi import FastAPI

from . import feedback, impact, mapping, nl_router, optimizer, scoring

app = FastAPI(title="RiskAlign-AI API")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/summary")
def get_summary() -> dict[str, str]:
    """Placeholder summary endpoint that will be wired to reporting later."""
    return {"summary": "Summary generation is not implemented yet."}


__all__ = [
    "app",
]
