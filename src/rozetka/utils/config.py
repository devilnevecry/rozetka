"""Application configuration helpers."""
from __future__ import annotations

import json
import os
from pathlib import Path

APP_NAME = "Rozetka"


def data_dir() -> Path:
    base = Path(os.environ.get("APPDATA", Path.home()))
    d = base / APP_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


def db_path() -> Path:
    return data_dir() / "rozetka.db"


def load_json(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")