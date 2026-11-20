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
from ..utils.i18n import t


class HistoryView(QWidget):
    def __init__(self, main) -> None:
        super().__init__()
        self.main = main
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)
        totals = QHBoxLayout()
        self.total_cost_lbl = QLabel(t("total_cost", v=0.0, cur=""))
        self.total_kwh_lbl = QLabel(t("total_kwh", v=0.0))
        totals.addWidget(self.total_cost_lbl)
        totals.addWidget(self.total_kwh_lbl)
        totals.addStretch()
        refresh_btn = QPushButton(t("btn_refresh"))
        refresh_btn.clicked.connect(self._refresh)
        totals.addWidget(refresh_btn)
        layout.addLayout(totals)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([t("col_id"), t("col_start"), t("col_end"), t("col_boot"), t("col_kwh"), t("col_cost")])
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
            self.table.setItem(i, 2, QTableWidgetItem(str(r.end_ts) if r.end_ts else t("running")))
            self.table.setItem(i, 3, QTableWidgetItem(t("yes") if r.is_boot else t("no")))
            self.table.setItem(i, 4, QTableWidgetItem(f"{r.energy_kwh:.4f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{r.cost:.4f}"))
        self.total_cost_lbl.setText(t("total_cost", v=repo.total_cost(), cur=self.main.tariff.currency))
        self.total_kwh_lbl.setText(t("total_kwh", v=repo.total_kwh()))

    def retranslate(self) -> None:
        self.table.setHorizontalHeaderLabels([t("col_id"), t("col_start"), t("col_end"), t("col_boot"), t("col_kwh"), t("col_cost")])
