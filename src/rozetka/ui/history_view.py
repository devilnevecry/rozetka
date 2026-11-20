"""History view with session list and totals."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..db.repository import Repository


class HistoryView(QWidget):
    def __init__(self, main) -> None:
        super().__init__()
        self.main = main
        layout = QVBoxLayout(self)
        totals = QHBoxLayout()
        self.total_cost_lbl = QLabel("Total cost: 0")
        self.total_kwh_lbl = QLabel("Total kWh: 0")
        totals.addWidget(self.total_cost_lbl)
        totals.addWidget(self.total_kwh_lbl)
        totals.addStretch()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh)
        totals.addWidget(refresh_btn)
        layout.addLayout(totals)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Start", "End", "Boot", "kWh", "Cost"])
        layout.addWidget(self.table)

    def refresh(self, repo: Repository, tracker) -> None:
        self._render(repo)

    def _refresh(self) -> None:
        self._render(self.main.repo)

    def _render(self, repo: Repository) -> None:
        rows = repo.list_sessions()
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(r.id)))
            self.table.setItem(i, 1, QTableWidgetItem(str(r.start_ts)))
            self.table.setItem(i, 2, QTableWidgetItem(str(r.end_ts) if r.end_ts else "running"))
            self.table.setItem(i, 3, QTableWidgetItem("yes" if r.is_boot else "no"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{r.energy_kwh:.4f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{r.cost:.4f}"))
        self.total_cost_lbl.setText(f"Total cost: {repo.total_cost():.4f} {self.main.tariff.currency}")
        self.total_kwh_lbl.setText(f"Total kWh: {repo.total_kwh():.4f}")