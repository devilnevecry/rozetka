"""Entry point."""
from __future__ import annotations

import ctypes
import sys
from pathlib import Path

import customtkinter as ctk

from .ui.main_window import MainWindow


def main() -> int:
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Rozetka.PowerTracker.1")
    except Exception:
        pass
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = MainWindow()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
