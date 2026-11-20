"""Settings view (CustomTkinter)."""
from __future__ import annotations

import customtkinter as ctk

from ..utils.autostart import disable as disable_autostart, enable as enable_autostart, is_enabled
from ..utils.i18n import LANGUAGES, get_language, set_language, t


class SettingsView(ctk.CTkFrame):
    def __init__(self, main) -> None:
        super().__init__(main.content, fg_color="transparent")
        self.main = main
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text=t("lbl_tariff")).grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.tariff_spin = ctk.CTkEntry(self, width=100)
        self.tariff_spin.insert(0, str(main.tariff.price_per_kwh))
        self.tariff_spin.grid(row=0, column=1, padx=8, pady=8, sticky="w")

        ctk.CTkLabel(self, text=t("lbl_currency")).grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.currency_edit = ctk.CTkEntry(self, width=100)
        self.currency_edit.insert(0, main.tariff.currency)
        self.currency_edit.grid(row=1, column=1, padx=8, pady=8, sticky="w")

        ctk.CTkLabel(self, text=t("lbl_language")).grid(row=2, column=0, padx=8, pady=8, sticky="w")
        self.lang_combo = ctk.CTkComboBox(self, values=list(LANGUAGES.values()))
        self.lang_combo.grid(row=2, column=1, padx=8, pady=8, sticky="w")
        # map
        self._code_by_name = {v: k for k, v in LANGUAGES.items()}
        self._name_by_code = {k: v for k, v in LANGUAGES.items()}
        self.lang_combo.set(self._name_by_code.get(get_language(), "English"))
        self.lang_combo.configure(command=self._on_language_changed)

        self.autostart_cb = ctk.CTkCheckBox(self, text="Start with Windows", command=self._toggle_autostart)
        self.autostart_cb.grid(row=3, column=0, columnspan=2, padx=8, pady=8, sticky="w")
        if is_enabled():
            self.autostart_cb.select()

        btn = ctk.CTkButton(self, text=t("btn_save"), command=self._save)
        btn.grid(row=4, column=0, padx=8, pady=8, sticky="w")

        # links at bottom
        link = ctk.CTkLabel(self, text="GitHub: devilnevecry/rozetka", text_color="#2563eb", cursor="hand2")
        link.grid(row=5, column=0, columnspan=2, padx=8, pady=(20, 2), sticky="w")
        link.bind("<Button-1>", lambda e: __import__("webbrowser").open("https://github.com/devilnevecry/rozetka"))

    def _save(self) -> None:
        try:
            self.main.tariff.price_per_kwh = float(self.tariff_spin.get())
        except ValueError:
            pass
        self.main.tariff.currency = self.currency_edit.get() or "RUB"
        self.main.repo.set_setting("tariff", str(self.main.tariff.price_per_kwh))
        self.main.repo.set_setting("currency", self.main.tariff.currency)

    def _on_language_changed(self, choice: str) -> None:
        code = self._code_by_name.get(choice)
        if code and code != get_language():
            set_language(code)
            self.main.repo.set_setting("language", code)
            self.main.rebuild_ui()

    def _toggle_autostart(self) -> None:
        if self.autostart_cb.get():
            enable_autostart()
        else:
            disable_autostart()

    def retranslate(self) -> None:
        pass
