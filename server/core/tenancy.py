"""Namespace/tenant helpers."""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import Request

_DEFAULT_NAMESPACE = os.getenv("DEFAULT_NAMESPACE", "default")
_OUTPUT_ROOT = Path(__file__).resolve().parent.parent / "output"
_CONFIG_ROOT = Path(__file__).resolve().parent.parent / "config" / "namespaces"


def get_namespace(request: Request | None) -> str:
    """Resolve the namespace from the request headers or fallback env."""
    if request is None:
        return _DEFAULT_NAMESPACE
    header_value = request.headers.get("X-Namespace")
    namespace = (header_value or "").strip()
    return namespace or _DEFAULT_NAMESPACE


def ensure_namespace_dirs(namespace: str) -> None:
    """Ensure the namespace output/config directories exist."""
    (_OUTPUT_ROOT / namespace).mkdir(parents=True, exist_ok=True)
    (_CONFIG_ROOT / namespace).mkdir(parents=True, exist_ok=True)


def output_path(namespace: str) -> Path:
    """Return the output directory for a namespace, creating it if needed."""
    ensure_namespace_dirs(namespace)
    return _OUTPUT_ROOT / namespace


def namespace_ai_config_path(namespace: str) -> Path:
    """Return the path to the namespace AI configuration file."""
    ensure_namespace_dirs(namespace)
    return _CONFIG_ROOT / namespace / "ai.json"


__all__ = ["get_namespace", "output_path", "namespace_ai_config_path", "ensure_namespace_dirs"]
