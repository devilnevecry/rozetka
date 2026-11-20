"""History view (CustomTkinter)."""
from __future__ import annotations

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

from ..utils.i18n import t


class HistoryView(ctk.CTkFrame):
    def __init__(self, main) -> None:
        super().__init__(main.content, fg_color="transparent")
        self.main = main
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        self.total_cost_lbl = ctk.CTkLabel(top, text=t("total_cost", v=0.0, cur=""))
        self.total_cost_lbl.grid(row=0, column=0, padx=4)
        self.total_kwh_lbl = ctk.CTkLabel(top, text=t("total_kwh", v=0.0))
        self.total_kwh_lbl.grid(row=0, column=1, padx=4)
        btn = ctk.CTkButton(top, text=t("btn_refresh"), command=self._refresh)
        btn.grid(row=0, column=2, padx=4)

        self.table = ttk.Treeview(self, columns=("id", "start", "end", "boot", "kwh", "cost"), show="headings")
        for col, name in zip(("id", "start", "end", "boot", "kwh", "cost"),
                             (t("col_id"), t("col_start"), t("col_end"), t("col_boot"), t("col_kwh"), t("col_cost"))):
            self.table.heading(col, text=name)
        self.table.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        sb = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=sb.set)
        sb.grid(row=1, column=1, sticky="ns", pady=8)

    def refresh(self, repo, tracker) -> None:
        self._render(repo)

    def _refresh(self) -> None:
        self._render(self.main.repo)

    def _render(self, repo) -> None:
        for item in self.table.get_children():
            self.table.delete(item)
        for r in repo.list_sessions():
            self.table.insert("", "end", values=(r.id, str(r.start_ts), str(r.end_ts) if r.end_ts else t("running"),
                                                t("yes") if r.is_boot else t("no"), f"{r.energy_kwh:.4f}", f"{r.cost:.4f}"))
        self.total_cost_lbl.configure(text=t("total_cost", v=repo.total_cost(), cur=self.main.tariff.currency))
        self.total_kwh_lbl.configure(text=t("total_kwh", v=repo.total_kwh()))

    def retranslate(self) -> None:
        pass
