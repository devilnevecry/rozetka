"""Settings view: tariff, currency, language."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..utils.i18n import LANGUAGES, get_language, set_language, t


class SettingsView(QWidget):
    def __init__(self, main) -> None:
        super().__init__()
        self.main = main
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        self.lbl_tariff = QLabel(t("lbl_tariff"))
        row.addWidget(self.lbl_tariff)
        self.tariff_spin = QDoubleSpinBox()
        self.tariff_spin.setRange(0, 10000)
        self.tariff_spin.setValue(main.tariff.price_per_kwh)
        row.addWidget(self.tariff_spin)
        self.lbl_currency = QLabel(t("lbl_currency"))
        row.addWidget(self.lbl_currency)
        self.currency_edit = QLineEdit(main.tariff.currency)
        row.addWidget(self.currency_edit)
        save = QPushButton(t("btn_save"))
        save.clicked.connect(self._save)
        row.addWidget(save)
        row.addStretch()
        layout.addLayout(row)

        lang_row = QHBoxLayout()
        self.lbl_language = QLabel(t("lbl_language"))
        lang_row.addWidget(self.lbl_language)
        self.lang_combo = QComboBox()
        for code, name in LANGUAGES.items():
            self.lang_combo.addItem(name, code)
        idx = self.lang_combo.findData(get_language())
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        lang_row.addWidget(self.lang_combo)
        lang_row.addStretch()
        layout.addLayout(lang_row)
        layout.addStretch()

    def _save(self) -> None:
        self.main.tariff.price_per_kwh = self.tariff_spin.value()
        self.main.tariff.currency = self.currency_edit.text() or "RUB"
        self.main.repo.set_setting("tariff", str(self.main.tariff.price_per_kwh))
        self.main.repo.set_setting("currency", self.main.tariff.currency)
        code = self.lang_combo.currentData()
        if code:
            set_language(code)
            self.main.repo.set_setting("language", code)
            self.main.retranslate()

    def retranslate(self) -> None:
        self.lbl_tariff.setText(t("lbl_tariff"))
        self.lbl_currency.setText(t("lbl_currency"))
        self.lbl_language.setText(t("lbl_language"))
