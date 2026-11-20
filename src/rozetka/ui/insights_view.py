"""Insights view: forecast, recommendations, alerts, export."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QDoubleSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.components import ComponentCategory
from ..db.repository import Repository
from ..utils.i18n import t


class InsightsView(QWidget):
    def __init__(self, main) -> None:
        super().__init__()
        self.main = main
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # threshold alert
        row = QHBoxLayout()
        row.addWidget(QLabel(t("threshold")))
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0, 100000)
        self.threshold_spin.setValue(float(self.main.repo.get_setting("threshold", "300") or 300))
        row.addWidget(self.threshold_spin)
        save_thr = QPushButton(t("btn_save"))
        save_thr.clicked.connect(self._save_threshold)
        row.addWidget(save_thr)
        row.addStretch()
        layout.addLayout(row)

        self.forecast_lbl = QLabel("")
        self.forecast_lbl.setStyleSheet("font-size: 12pt; font-weight: 600; color: #8fb3ff;")
        layout.addWidget(self.forecast_lbl)

        self.sessions_lbl = QLabel("")
        layout.addWidget(self.sessions_lbl)

        self.reco_text = QTextEdit()
        self.reco_text.setReadOnly(True)
        layout.addWidget(self.reco_text, stretch=1)

        btn_row = QHBoxLayout()
        export_btn = QPushButton(t("export_csv"))
        export_btn.clicked.connect(self._export_csv)
        btn_row.addWidget(export_btn)
        refresh_btn = QPushButton(t("btn_refresh"))
        refresh_btn.clicked.connect(self.refresh)
        btn_row.addWidget(refresh_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.refresh()

    def refresh(self) -> None:
        repo = self.main.repo
        sessions = repo.list_sessions()
        total_kwh = repo.total_kwh()
        total_cost = repo.total_cost()
        n = len(sessions)
        # average watts
        if sessions:
            avg_w = sum((s.avg_watts or 0) for s in sessions) / len(sessions)
        else:
            avg_w = 0.0
        # monthly forecast: avg_w * 24 * 30 / 1000 * tariff
        monthly_kwh = avg_w * 24 * 30 / 1000.0
        monthly_cost = monthly_kwh * self.main.tariff.price_per_kwh
        self.forecast_lbl.setText(t("monthly_forecast") + f": {monthly_cost:.2f} {self.main.tariff.currency} ({monthly_kwh:.1f} kWh)")
        self.sessions_lbl.setText(t("sessions_count", n=n) + f" | {t('total_kwh', v=total_kwh)} | {t('total_cost', v=total_cost, cur=self.main.tariff.currency)}")
        # battery
        try:
            batt = __import__("psutil").sensors_battery()
            if batt is not None:
                lines_battery = f"Battery: {batt.percent:.0f}% ({'charging' if batt.power_plugged else 'discharging'})"
            else:
                lines_battery = "Battery: n/a (desktop)"
        except Exception:
            lines_battery = "Battery: n/a"
        # top processes
        try:
            import psutil
            procs = sorted(psutil.process_iter(['pid','name','cpu_percent','memory_percent']),
                           key=lambda x: x.info.get('cpu_percent') or 0, reverse=True)[:5]
            top_lines = ["Top processes by CPU:"]
            for pr in procs:
                info = pr.info
                top_lines.append(f"  {info.get('name','?')} (PID {info.get('pid')}) - CPU {info.get('cpu_percent',0):.1f}%  RAM {info.get('memory_percent',0):.1f}%")
        except Exception:
            top_lines = ["Top processes: n/a"]
        # CO2
        co2 = total_kwh * 0.4
        # recommendations
        lines = []
        reg = self.main.registry
        for c in reg.components:
            if c.category == ComponentCategory.CPU and c.current_watts > c.tdp_watts * 0.8:
                lines.append("- CPU near TDP: consider better cooling or undervolting.")
            if c.category == ComponentCategory.GPU and c.current_watts > c.tdp_watts * 0.8:
                lines.append("- GPU high load: limit FPS or reduce settings to save power.")
        if avg_w > 200:
            lines.append("- Average power high: enable power-saving plan in OS.")
        if not lines:
            lines.append("- System running efficiently. No action needed.")
        # threshold check
        thr = float(self.main.repo.get_setting("threshold", "300") or 300)
        if self.main._last_power_watts > thr:
            lines.insert(0, f"! Current power {self.main._last_power_watts:.0f} W exceeds threshold {thr:.0f} W.")
        extra = [lines_battery, "", "CO2 estimate: {:.2f} kg".format(co2), ""] + top_lines + [""]
        self.reco_text.setPlainText("\n".join(extra + lines))

    def _save_threshold(self) -> None:
        self.main.repo.set_setting("threshold", str(self.threshold_spin.value()))
        self.refresh()

    def _export_csv(self) -> None:
        import os
        path = os.path.join(str(self.main.repo.get_setting("export_path", "") or ""), "rozetka_history.csv")
        # simple: save to data dir
        from pathlib import Path
        out = Path(self.main.repo.get_setting("export_path", "") or ".") / "rozetka_history.csv"
        # fallback to home
        if not out.parent.exists():
            out = Path.home() / "rozetka_history.csv"
        try:
            with open(out, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["id", "start", "end", "boot", "kwh", "cost", "avg_watts", "duration_s"])
                for r in self.main.repo.list_sessions():
                    w.writerow([r.id, r.start_ts, r.end_ts, r.is_boot, r.energy_kwh, r.cost, r.avg_watts, r.duration_s])
            QMessageBox.information(self, "Export", f"Saved to {out}")
        except Exception as e:
            QMessageBox.warning(self, "Export", str(e))

    def retranslate(self) -> None:
        self.threshold_spin.setToolTip(t("threshold"))
