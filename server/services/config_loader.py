from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def _load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_scoring_config(overrides: Optional[Dict[str, float]] = None) -> Dict:
    config = _load_json(CONFIG_DIR / "scoring.json")
    if overrides:
        config["weights"].update(overrides)
    return config


def load_controls_mapping(framework: str) -> Optional[Dict[str, Dict[str, str]]]:
    mapping_path = CONFIG_DIR / f"controls_{framework.lower()}.json"
    if not mapping_path.exists():
        return None
    return _load_json(mapping_path)
