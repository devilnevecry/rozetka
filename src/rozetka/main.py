"""Entry point."""
from __future__ import annotations

import ctypes
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow


def main() -> int:
    # Windows taskbar icon grouping
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Rozetka.PowerTracker.1")
    except Exception:
        pass
    app = QApplication(sys.argv)
    app.setApplicationName("Rozetka")
    icon_path = Path(__file__).resolve().parents[2] / "resources" / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    window = MainWindow()
    window.showNormal()
    window.activateWindow()
    window.raise_()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
