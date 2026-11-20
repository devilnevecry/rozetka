"""Application stylesheet (modern dark theme)."""
from __future__ import annotations

DARK_QSS = r"""
QWidget {
    background-color: #1e2230;
    color: #e6e9f0;
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 10pt;
}
QMainWindow { background-color: #161a26; }
QTabWidget::pane { border: 1px solid #2a3148; border-radius: 8px; background: #1e2230; }
QTabBar::tab {
    background: #252b3d; color: #a8b0c4; padding: 8px 18px; margin-right: 4px;
    border-top-left-radius: 8px; border-top-right-radius: 8px;
}
QTabBar::tab:selected { background: #3a4a7a; color: #ffffff; }
QTabBar::tab:hover { background: #2f3a5a; }
QGroupBox {
    border: 1px solid #2a3148; border-radius: 8px; margin-top: 12px;
    padding: 10px; background: #252b3d; font-weight: 600;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color: #8fb3ff; }
QLabel { color: #e6e9f0; }
QPushButton {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #4a6cf7, stop:1 #3451d1);
    color: white; border: none; border-radius: 6px; padding: 6px 14px; font-weight: 600;
}
QPushButton:hover { background: #5a7cff; }
QPushButton:pressed { background: #2a41b1; }
QDoubleSpinBox, QLineEdit, QComboBox {
    background: #2a3148; border: 1px solid #3a4568; border-radius: 6px;
    padding: 4px 8px; color: #e6e9f0;
}
QTableWidget {
    background: #1e2230; alternate-background-color: #252b3d;
    gridline-color: #2a3148; border: 1px solid #2a3148; border-radius: 6px;
}
QHeaderView::section {
    background: #2a3148; color: #8fb3ff; padding: 6px; border: none; font-weight: 600;
}
QStatusBar { background: #161a26; color: #a8b0c4; }
QScrollBar:vertical { background: #1e2230; width: 10px; }
QScrollBar::handle:vertical { background: #3a4568; border-radius: 5px; }
"""
