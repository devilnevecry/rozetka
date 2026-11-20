"""Autostart helpers (Windows startup folder)."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _startup_dir() -> Path:
    return Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _bat_path() -> Path:
    return _startup_dir() / "Rozetka.bat"


def is_enabled() -> bool:
    return _bat_path().exists()


def enable() -> None:
    python = sys.executable.replace("python.exe", "pythonw.exe")
    if not Path(python).exists():
        python = sys.executable
    src = Path(__file__).resolve().parents[2] / "src"
    project = Path(__file__).resolve().parents[2]
    lines = [
        "@echo off",
        f'set "PYTHONPATH={src}"',
        f'cd /d "{project}"',
        f'"{python}" -m rozetka.main',
    ]
    _startup_dir().mkdir(parents=True, exist_ok=True)
    _bat_path().write_text("\n".join(lines) + "\n", encoding="utf-8")


def disable() -> None:
    try:
        _bat_path().unlink()
    except FileNotFoundError:
        pass
