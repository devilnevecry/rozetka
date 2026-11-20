"""Settings view: tariff, currency."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SettingsView(QWidget):
    def __init__(self, main) -> None:
        super().__init__()
        self.main = main
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        row.addWidget(QLabel("Price per kWh:"))
        self.tariff_spin = QDoubleSpinBox()
        self.tariff_spin.setRange(0, 10000)
        self.tariff_spin.setValue(main.tariff.price_per_kwh)
        row.addWidget(self.tariff_spin)
        row.addWidget(QLabel("Currency:"))
        self.currency_edit = QLineEdit(main.tariff.currency)
        row.addWidget(self.currency_edit)
        save = QPushButton("Save")
        save.clicked.connect(self._save)
        row.addWidget(save)
        row.addStretch()
        layout.addLayout(row)
        layout.addStretch()

    def _save(self) -> None:
        self.main.tariff.price_per_kwh = self.tariff_spin.value()
        self.main.tariff.currency = self.currency_edit.text() or "RUB"
        self.main.repo.set_setting("tariff", str(self.main.tariff.price_per_kwh))
        self.main.repo.set_setting("currency", self.main.tariff.currency)