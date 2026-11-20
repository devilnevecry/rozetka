"""Settings view: tariff, currency, language, autostart, links."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices, QCursor
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..utils.autostart import disable as disable_autostart, enable as enable_autostart, is_enabled
from ..utils.i18n import LANGUAGES, get_language, set_language, t


class SettingsView(QWidget):
    def __init__(self, main) -> None:
        super().__init__()
        self.main = main
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

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
        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_row.addWidget(self.lang_combo)
        lang_row.addStretch()
        layout.addLayout(lang_row)

        # autostart
        self.autostart_cb = QCheckBox("Start with Windows")
        self.autostart_cb.setChecked(is_enabled())
        self.autostart_cb.toggled.connect(self._toggle_autostart)
        layout.addWidget(self.autostart_cb)

        layout.addStretch()

        # links at bottom
        links = QVBoxLayout()
        git_lbl = QLabel('<a href="https://github.com/devilnevecry/rozetka" style="color:#2563eb;">GitHub: devilnevecry/rozetka</a>')
        git_lbl.setOpenExternalLinks(True)
        git_lbl.setCursor(QCursor(Qt.PointingHandCursor))
        links.addWidget(git_lbl)
        crypto_lbl = QLabel("Crypto wallet (placeholder): 0x0000000000000000000000000000000000000000")
        crypto_lbl.setStyleSheet("color: #8a8f9e; font-size: 9pt;")
        crypto_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        links.addWidget(crypto_lbl)
        layout.addLayout(links)

    def _save(self) -> None:
        self.main.tariff.price_per_kwh = self.tariff_spin.value()
        self.main.tariff.currency = self.currency_edit.text() or "RUB"
        self.main.repo.set_setting("tariff", str(self.main.tariff.price_per_kwh))
        self.main.repo.set_setting("currency", self.main.tariff.currency)

    def _on_language_changed(self, _index: int) -> None:
        code = self.lang_combo.currentData()
        if code and code != get_language():
            set_language(code)
            self.main.repo.set_setting("language", code)
            self.main.rebuild_ui()

    def _toggle_autostart(self, checked: bool) -> None:
        if checked:
            enable_autostart()
        else:
            disable_autostart()

    def retranslate(self) -> None:
        self.lbl_tariff.setText(t("lbl_tariff"))
        self.lbl_currency.setText(t("lbl_currency"))
        self.lbl_language.setText(t("lbl_language"))
