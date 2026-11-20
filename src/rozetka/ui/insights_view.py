"""Insights view (CustomTkinter)."""
from __future__ import annotations

import customtkinter as ctk

from ..utils.i18n import t


class InsightsView(ctk.CTkFrame):
    def __init__(self, main) -> None:
        super().__init__(main.content, fg_color="transparent")
        self.main = main
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.forecast_lbl = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=13, weight="bold"), text_color="#2563eb")
        self.forecast_lbl.grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.sessions_lbl = ctk.CTkLabel(self, text="", text_color="#8a8f9e")
        self.sessions_lbl.grid(row=1, column=0, padx=8, pady=4, sticky="w")

        self.reco_text = ctk.CTkTextbox(self, height=200)
        self.reco_text.grid(row=2, column=0, padx=8, pady=8, sticky="nsew")

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=3, column=0, padx=8, pady=8, sticky="w")
        ctk.CTkButton(btns, text=t("export_csv"), command=self._export_csv).grid(row=0, column=0, padx=4)
        ctk.CTkButton(btns, text=t("btn_refresh"), command=self.refresh).grid(row=0, column=1, padx=4)

        self.refresh()

    def refresh(self) -> None:
        import psutil
        repo = self.main.repo
        sessions = repo.list_sessions()
        total_kwh = repo.total_kwh()
        total_cost = repo.total_cost()
        n = len(sessions)
        if sessions:
            avg_w = sum((s.avg_watts or 0) for s in sessions) / len(sessions)
        else:
            avg_w = 0.0
        monthly_kwh = avg_w * 24 * 30 / 1000.0
        monthly_cost = monthly_kwh * self.main.tariff.price_per_kwh
        self.forecast_lbl.configure(text=t("monthly_forecast") + f": {monthly_cost:.2f} {self.main.tariff.currency} ({monthly_kwh:.1f} kWh)")
        self.sessions_lbl.configure(text=t("sessions_count", n=n) + f" | {t('total_kwh', v=total_kwh)} | {t('total_cost', v=total_cost, cur=self.main.tariff.currency)}")

        lines = []
        try:
            batt = psutil.sensors_battery()
            if batt is not None:
                lines.append(f"Battery: {batt.percent:.0f}% ({'charging' if batt.power_plugged else 'discharging'})")
            else:
                lines.append("Battery: n/a (desktop)")
        except Exception:
            lines.append("Battery: n/a")
        try:
            procs = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
                           key=lambda x: x.info.get('cpu_percent') or 0, reverse=True)[:5]
            lines.append("Top processes by CPU:")
            for pr in procs:
                info = pr.info
                lines.append(f"  {info.get('name', '?')} (PID {info.get('pid')}) - CPU {info.get('cpu_percent', 0):.1f}%  RAM {info.get('memory_percent', 0):.1f}%")
        except Exception:
            lines.append("Top processes: n/a")
        co2 = total_kwh * 0.4
        lines.append(f"CO2 estimate: {co2:.2f} kg")
        lines.append("")
        reg = self.main.registry
        for c in reg.components:
            if c.category.value == "cpu" and c.current_watts > c.tdp_watts * 0.8:
                lines.append("- CPU near TDP: consider better cooling or undervolting.")
            if c.category.value == "gpu" and c.current_watts > c.tdp_watts * 0.8:
                lines.append("- GPU high load: limit FPS or reduce settings to save power.")
        if avg_w > 200:
            lines.append("- Average power high: enable power-saving plan in OS.")
        if not any(l.startswith("-") for l in lines):
            lines.append("- System running efficiently. No action needed.")
        thr = float(self.main.repo.get_setting("threshold", "300") or 300)
        if self.main._last_power_watts > thr:
            lines.insert(0, f"! Current power {self.main._last_power_watts:.0f} W exceeds threshold {thr:.0f} W.")
        self.reco_text.delete("1.0", "end")
        self.reco_text.insert("1.0", "\n".join(lines))

    def _export_csv(self) -> None:
        import csv
        from pathlib import Path
        out = Path.home() / "rozetka_history.csv"
        try:
            with open(out, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["id", "start", "end", "boot", "kwh", "cost", "avg_watts", "duration_s"])
                for r in self.main.repo.list_sessions():
                    w.writerow([r.id, r.start_ts, r.end_ts, r.is_boot, r.energy_kwh, r.cost, r.avg_watts, r.duration_s])
            import tkinter.messagebox as mb
            mb.showinfo("Export", f"Saved to {out}")
        except Exception as e:
            import tkinter.messagebox as mb
            mb.showerror("Export", str(e))

    def retranslate(self) -> None:
        pass
