"""Application stylesheet (clean professional dark theme)."""
from __future__ import annotations

DARK_QSS = r"""
* { font-family: "Segoe UI", "Inter", sans-serif; }

QWidget {
    background-color: #0b0d12;
    color: #e4e6eb;
    font-size: 10pt;
}
QMainWindow { background-color: #0b0d12; }

QTabWidget::pane {
    border: 1px solid #1f2330;
    border-radius: 6px;
    background: #0b0d12;
    margin-top: 4px;
}
QTabBar::tab {
    background: transparent;
    color: #8a8f9e;
    padding: 8px 16px;
    margin-right: 2px;
    border-bottom: 2px solid transparent;
    font-weight: 500;
}
QTabBar::tab:selected {
    color: #ffffff;
    border-bottom: 2px solid #2563eb;
}
QTabBar::tab:hover { color: #c8ccd6; }

QGroupBox {
    border: 1px solid #1f2330;
    border-radius: 6px;
    margin-top: 12px;
    padding: 12px;
    background: #11141b;
    font-weight: 600;
    color: #c8ccd6;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
    color: #8a8f9e;
    font-size: 9pt;
    font-weight: 600;
    text-transform: uppercase;
}

QLabel { color: #e4e6eb; }

QPushButton {
    background: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: 500;
}
QPushButton:hover { background: #1d4ed8; }
QPushButton:pressed { background: #1e40af; }
QPushButton:flat { background: transparent; color: #2563eb; }

QDoubleSpinBox, QLineEdit, QComboBox {
    background: #11141b;
    border: 1px solid #1f2330;
    border-radius: 4px;
    padding: 5px 8px;
    color: #e4e6eb;
}
QDoubleSpinBox:focus, QLineEdit:focus, QComboBox:focus {
    border: 1px solid #2563eb;
}

QTableWidget {
    background: #11141b;
    alternate-background-color: #141821;
    gridline-color: #1f2330;
    border: 1px solid #1f2330;
    border-radius: 4px;
}
QHeaderView::section {
    background: #0b0d12;
    color: #8a8f9e;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #1f2330;
    font-weight: 600;
    font-size: 9pt;
    text-transform: uppercase;
}

QStatusBar {
    background: #0b0d12;
    color: #8a8f9e;
    border-top: 1px solid #1f2330;
}

QScrollBar:vertical { background: #0b0d12; width: 8px; }
QScrollBar::handle:vertical { background: #2a2f3d; border-radius: 4px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #3a4050; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QProgressBar {
    background: #1f2330;
    border: none;
    border-radius: 3px;
    text-align: center;
    color: #8a8f9e;
    font-size: 8pt;
    height: 6px;
}
QProgressBar::chunk {
    background: #2563eb;
    border-radius: 3px;
}

QTextEdit {
    background: #11141b;
    border: 1px solid #1f2330;
    border-radius: 4px;
    padding: 8px;
    color: #e4e6eb;
}

QToolTip {
    background: #1f2330;
    color: #e4e6eb;
    border: 1px solid #2a2f3d;
    border-radius: 4px;
    padding: 4px 8px;
}
"""
