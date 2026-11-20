"""Components view (CustomTkinter)."""
from __future__ import annotations

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

from ..utils.i18n import t


class ComponentsView(ctk.CTkFrame):
    def __init__(self, main) -> None:
        super().__init__(main.content, fg_color="transparent")
        self.main = main
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Edit form
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        ctk.CTkLabel(form, text=t("col_name")).grid(row=0, column=0, padx=4)
        self.comp_combo = ctk.CTkComboBox(form, values=[])
        self.comp_combo.grid(row=0, column=1, padx=4)
        ctk.CTkLabel(form, text=t("col_tdp")).grid(row=0, column=2, padx=4)
        self.tdp_entry = ctk.CTkEntry(form, width=80)
        self.tdp_entry.grid(row=0, column=3, padx=4)
        btn = ctk.CTkButton(form, text=t("btn_save_tdp"), command=self._save)
        btn.grid(row=0, column=4, padx=4)

        self.table = ttk.Treeview(self, columns=("name", "category", "tdp", "load", "current"), show="headings")
        for col, name in zip(("name", "category", "tdp", "load", "current"),
                             (t("col_name"), t("col_category"), t("col_tdp"), t("col_load"), t("col_current"))):
            self.table.heading(col, text=name)
        self.table.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        sb = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=sb.set)
        sb.grid(row=1, column=1, sticky="ns", pady=8)

        # description
        self.desc = ctk.CTkLabel(self, text="", text_color="#8a8f9e", wraplength=600, justify="left")
        self.desc.grid(row=2, column=0, padx=8, pady=4, sticky="w")
        self.table.bind("<<TreeviewSelect>>", self._on_select)

    def refresh(self, reg) -> None:
        for item in self.table.get_children():
            self.table.delete(item)
        names = []
        for c in reg.components:
            self.table.insert("", "end", values=(c.name, c.category.value, f"{c.tdp_watts:.1f}", f"{c.load*100:.1f}", f"{c.current_watts:.1f}"))
            names.append(c.name)
        self.comp_combo.configure(values=names)
        if names and not self.comp_combo.get():
            self.comp_combo.set(names[0])

    def _on_select(self, _event) -> None:
        sel = self.table.selection()
        if not sel:
            return
        vals = self.table.item(sel[0], "values")
        self.desc.configure(text=f"{vals[0]}: {vals[1]} | TDP {vals[2]} W | Load {vals[3]}% | Now {vals[4]} W")

    def _save(self) -> None:
        name = self.comp_combo.get()
        try:
            tdp = float(self.tdp_entry.get())
        except ValueError:
            return
        reg = self.main.registry
        for c in reg.components:
            if c.name == name:
                c.tdp_watts = tdp
                self.main.repo.upsert_component(c.name, c.category.value, c.tdp_watts, c.idle_watts)
        self.refresh(reg)
        self.tdp_entry.delete(0, "end")

    def retranslate(self) -> None:
        pass
