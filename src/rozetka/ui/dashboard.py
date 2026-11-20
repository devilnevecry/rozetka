"""Dashboard view with live metrics, multi-series chart and component bar chart."""
from __future__ import annotations

from collections import deque

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
import pyqtgraph as pg

from ..core.components import ComponentRegistry
from ..core.monitor import SystemSnapshot
from ..utils.i18n import t


class DashboardView(QWidget):
    def __init__(self, main) -> None:
        super().__init__()
        self.main = main
        self._power_history = deque(maxlen=180)
        self._cpu_history = deque(maxlen=180)
        self._gpu_history = deque(maxlen=180)
        layout = QVBoxLayout(self)

        grid = QGridLayout()
        self.labels = {}
        metric_keys = ["metric_cpu_pct", "metric_cpu_temp", "metric_cpu_freq", "metric_ram_pct",
                      "metric_ram_used", "metric_disk_pct", "metric_disk_r", "metric_disk_w",
                      "metric_net_up", "metric_net_down", "metric_gpu_load", "metric_gpu_temp",
                      "metric_power", "metric_session_cost"]
        metrics = [t(k) for k in metric_keys]
        row = 0
        col = 0
        for k, m in zip(metric_keys, metrics):
            box = QGroupBox(m)
            lbl = QLabel("0")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 14pt; font-weight: 700; color: #8fb3ff;")
            v = QVBoxLayout()
            v.addWidget(lbl)
            box.setLayout(v)
            grid.addWidget(box, row, col)
            self.labels[k] = lbl
            col += 1
            if col >= 4:
                col = 0
                row += 1
        layout.addLayout(grid)

        self.power_label = QLabel("")
        self.power_label.setStyleSheet("font-size: 11pt; color: #a8b0c4;")
        layout.addWidget(self.power_label)

        # multi-series chart
        self.plot = pg.PlotWidget()
        self.plot.setBackground("#1e2230")
        self.plot.setTitle(t("chart_power"), color="#8fb3ff", size="12pt")
        self.plot.setLabel("left", "Value", color="#a8b0c4")
        self.plot.setLabel("bottom", "Samples", color="#a8b0c4")
        self.plot.addLegend()
        self.plot.showGrid(x=True, y=True, alpha=0.2)
        self.curve_power = self.plot.plot(pen=pg.mkPen("#ff6b6b", width=2), name="Power (W)")
        self.curve_cpu = self.plot.plot(pen=pg.mkPen("#4a6cf7", width=2), name="CPU %")
        self.curve_gpu = self.plot.plot(pen=pg.mkPen("#51cf66", width=2), name="GPU %")
        layout.addWidget(self.plot, stretch=2)

        # component bar chart
        self.bar_plot = pg.PlotWidget()
        self.bar_plot.setBackground("#1e2230")
        self.bar_plot.setTitle(t("pie_title"), color="#8fb3ff", size="12pt")
        self.bar_plot.setLabel("left", "Watts", color="#a8b0c4")
        layout.addWidget(self.bar_plot, stretch=1)

    def update_snapshot(self, snap, power_w, reg) -> None:
        self.labels["metric_cpu_pct"].setText(f"{snap.cpu.percent:.1f}")
        self.labels["metric_cpu_temp"].setText(f"{snap.cpu.temp_c:.1f} C" if snap.cpu.temp_c is not None else "n/a")
        self.labels["metric_cpu_freq"].setText(f"{snap.cpu.freq_mhz:.0f} MHz")
        self.labels["metric_ram_pct"].setText(f"{snap.memory.percent:.1f}")
        self.labels["metric_ram_used"].setText(f"{snap.memory.used_gb:.2f} GB")
        self.labels["metric_disk_pct"].setText(f"{snap.disk.percent:.1f}")
        self.labels["metric_disk_r"].setText(f"{snap.disk.read_bytes_s/1024:.1f} KB/s")
        self.labels["metric_disk_w"].setText(f"{snap.disk.write_bytes_s/1024:.1f} KB/s")
        self.labels["metric_net_up"].setText(f"{snap.net.sent_bytes_s/1024:.1f} KB/s")
        self.labels["metric_net_down"].setText(f"{snap.net.recv_bytes_s/1024:.1f} KB/s")
        if snap.gpus:
            g = snap.gpus[0]
            self.labels["metric_gpu_load"].setText(f"{g.load*100:.1f}")
            self.labels["metric_gpu_temp"].setText(f"{g.temp_c:.1f} C" if g.temp_c is not None else "n/a")
        else:
            self.labels["metric_gpu_load"].setText("n/a")
            self.labels["metric_gpu_temp"].setText("n/a")
        self.labels["metric_power"].setText(f"{power_w:.1f}")
        try:
            sess = self.main.tracker.current
            if sess is not None:
                kwh = sess.total_kwh()
                cost = kwh * self.main.tariff.price_per_kwh
                self.labels["metric_session_cost"].setText(f"{cost:.4f}")
        except Exception:
            pass
        self.power_label.setText(t("power_label", w=power_w, tdp=reg.total_tdp()))
        self._power_history.append(power_w)
        self._cpu_history.append(snap.cpu.percent)
        self._gpu_history.append((snap.gpus[0].load*100) if snap.gpus else 0.0)
        self.curve_power.setData(list(self._power_history))
        self.curve_cpu.setData(list(self._cpu_history))
        self.curve_gpu.setData(list(self._gpu_history))
        # bar chart
        names = [c.name[:12] for c in reg.components]
        vals = [c.current_watts for c in reg.components]
        bg = pg.BarGraphItem(x=range(len(names)), height=vals, width=0.6, brushes="#4a6cf7")
        self.bar_plot.clear()
        self.bar_plot.addItem(bg)
        # x axis labels
        ax = self.bar_plot.getAxis("bottom")
        ax.setTicks([[(i, n) for i, n in enumerate(names)]])

    def retranslate(self) -> None:
        self.plot.setTitle(t("chart_power"), color="#8fb3ff", size="12pt")
        self.bar_plot.setTitle(t("pie_title"), color="#8fb3ff", size="12pt")
