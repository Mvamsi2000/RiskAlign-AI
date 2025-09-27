from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=8)
def scoring_config() -> Dict[str, Any]:
    return _load_json(BASE_DIR / "config" / "scoring.json")


@lru_cache(maxsize=8)
def controls_mapping() -> Dict[str, Any]:
    return _load_json(BASE_DIR / "config" / "controls_cis.json")
