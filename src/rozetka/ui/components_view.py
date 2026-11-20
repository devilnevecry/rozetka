"""Components view: per-component TDP and current power."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core.components import ComponentRegistry
from ..utils.i18n import t


class ComponentsView(QWidget):
    def __init__(self, main) -> None:
        super().__init__()
        self.main = main
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([t("col_name"), t("col_category"), t("col_tdp"), t("col_load"), t("col_current")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton(t("btn_save_tdp"))
        self.save_btn.clicked.connect(self._save)
        btn_row.addWidget(self.save_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        self.tdp_spins: dict = {}

    def refresh(self, reg: ComponentRegistry) -> None:
        self.table.setRowCount(len(reg.components))
        for i, c in enumerate(reg.components):
            self.table.setItem(i, 0, QTableWidgetItem(c.name))
            self.table.setItem(i, 1, QTableWidgetItem(c.category.value))
            spin = QDoubleSpinBox()
            spin.setRange(0, 10000)
            spin.setValue(c.tdp_watts)
            self.table.setCellWidget(i, 2, spin)
            self.tdp_spins[c.name] = spin
            self.table.setItem(i, 3, QTableWidgetItem(f"{c.load*100:.1f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{c.current_watts:.1f}"))

    def _save(self) -> None:
        reg = self.main.registry
        for c in reg.components:
            spin = self.tdp_spins.get(c.name)
            if spin is not None:
                c.tdp_watts = spin.value()
                self.main.repo.upsert_component(c.name, c.category.value, c.tdp_watts, c.idle_watts)
        self.refresh(reg)

    def retranslate(self) -> None:
        self.table.setHorizontalHeaderLabels([t("col_name"), t("col_category"), t("col_tdp"), t("col_load"), t("col_current")])
        self.save_btn.setText(t("btn_save_tdp"))
