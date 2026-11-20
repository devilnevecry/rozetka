"""Application stylesheet (modern dark glass theme)."""
from __future__ import annotations

DARK_QSS = r"""
QWidget {
    background-color: #0f1220;
    color: #e8ecf4;
    font-family: "Segoe UI", "Inter", "Helvetica Neue", sans-serif;
    font-size: 10pt;
}
QMainWindow { background-color: #0f1220; }
QTabWidget::pane {
    border: 1px solid #232a42; border-radius: 12px; background: #0f1220;
    margin-top: 6px;
}
QTabBar::tab {
    background: #1a1f33; color: #8a93ad; padding: 10px 22px; margin-right: 6px;
    border-top-left-radius: 10px; border-top-right-radius: 10px; font-weight: 600;
}
QTabBar::tab:selected {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #4a6cf7, stop:1 #3451d1);
    color: #ffffff;
}
QTabBar::tab:hover { background: #232a42; color: #c8d0e4; }
QGroupBox {
    border: 1px solid #232a42; border-radius: 12px; margin-top: 14px;
    padding: 12px; background: #161b2e; font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin; left: 14px; padding: 0 6px; color: #7aa2ff;
    font-size: 10pt;
}
QLabel { color: #e8ecf4; }
QPushButton {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #4a6cf7, stop:1 #2f46c9);
    color: white; border: none; border-radius: 8px; padding: 8px 16px; font-weight: 600;
}
QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #5a7cff, stop:1 #3a56d9); }
QPushButton:pressed { background: #2a3fb5; }
QDoubleSpinBox, QLineEdit, QComboBox {
    background: #1a1f33; border: 1px solid #2a3148; border-radius: 8px;
    padding: 6px 10px; color: #e8ecf4;
}
QTableWidget {
    background: #161b2e; alternate-background-color: #1a1f33;
    gridline-color: #232a42; border: 1px solid #232a42; border-radius: 8px;
}
QHeaderView::section {
    background: #1a1f33; color: #7aa2ff; padding: 8px; border: none; font-weight: 700;
}
QStatusBar { background: #0a0d18; color: #8a93ad; border-top: 1px solid #232a42; }
QScrollBar:vertical { background: #0f1220; width: 10px; border-radius: 5px; }
QScrollBar::handle:vertical { background: #2a3148; border-radius: 5px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #3a4568; }
QProgressBar {
    background: #1a1f33; border: 1px solid #232a42; border-radius: 6px;
    text-align: center; color: #e8ecf4; height: 16px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4a6cf7, stop:1 #7aa2ff);
    border-radius: 5px;
}
QTextEdit {
    background: #161b2e; border: 1px solid #232a42; border-radius: 8px;
    padding: 8px; color: #e8ecf4;
}
QToolTip {
    background: #1a1f33; color: #e8ecf4; border: 1px solid #2a3148; border-radius: 6px;
    padding: 4px 8px;
}
"""
