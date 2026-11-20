"""Dashboard view with live metrics, progress bars and charts."""
from __future__ import annotations

from collections import deque

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
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

        # Hero power card
        hero = QGroupBox("")
        hero.setStyleSheet("QGroupBox { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1a1f33, stop:1 #232a42); border: 1px solid #4a6cf7; }")
        hero_layout = QHBoxLayout(hero)
        self.hero_power = QLabel("0 W")
        self.hero_power.setStyleSheet("font-size: 36pt; font-weight: 800; color: #7aa2ff;")
        hero_layout.addWidget(self.hero_power)
        hero_layout.addStretch()
        self.hero_bar = QProgressBar()
        self.hero_bar.setRange(0, 100)
        self.hero_bar.setValue(0)
        self.hero_bar.setFixedWidth(260)
        hero_layout.addWidget(self.hero_bar)
        self.power_label = QLabel("")
        self.power_label.setStyleSheet("color: #8a93ad;")
        hero_layout.addWidget(self.power_label)
        layout.addWidget(hero)

        # Progress bars for CPU/RAM/GPU
        pb_row = QHBoxLayout()
        for key, color in [("cpu", "#4a6cf7"), ("ram", "#51cf66"), ("gpu", "#ff6b6b")]:
            box = QGroupBox(key.upper())
            v = QVBoxLayout(box)
            bar = QProgressBar()
            bar.setStyleSheet(f"QProgressBar::chunk {{ background: {color}; }}")
            v.addWidget(bar)
            lbl = QLabel("0%")
            lbl.setAlignment(Qt.AlignCenter)
            v.addWidget(lbl)
            pb_row.addWidget(box)
            setattr(self, f"{key}_bar", bar)
            setattr(self, f"{key}_lbl", lbl)
        layout.addLayout(pb_row)

        # Metric cards grid
        grid = QGridLayout()
        self.labels = {}
        self.boxes = {}
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
            lbl.setStyleSheet("font-size: 15pt; font-weight: 700; color: #8fb3ff;")
            v = QVBoxLayout()
            v.addWidget(lbl)
            box.setLayout(v)
            grid.addWidget(box, row, col)
            self.labels[k] = lbl
            self.boxes[k] = box
            col += 1
            if col >= 4:
                col = 0
                row += 1
        layout.addLayout(grid)

        # multi-series chart
        self.plot = pg.PlotWidget()
        self.plot.setBackground("#161b2e")
        self.plot.setTitle(t("chart_power"), color="#7aa2ff", size="12pt")
        self.plot.setLabel("left", "Value", color="#8a93ad")
        self.plot.setLabel("bottom", "Samples", color="#8a93ad")
        self.plot.addLegend()
        self.plot.showGrid(x=True, y=True, alpha=0.15)
        self.curve_power = self.plot.plot(pen=pg.mkPen("#ff6b6b", width=2), name="Power (W)")
        self.curve_cpu = self.plot.plot(pen=pg.mkPen("#4a6cf7", width=2), name="CPU %")
        self.curve_gpu = self.plot.plot(pen=pg.mkPen("#51cf66", width=2), name="GPU %")
        layout.addWidget(self.plot, stretch=2)

        # component bar chart
        self.bar_plot = pg.PlotWidget()
        self.bar_plot.setBackground("#161b2e")
        self.bar_plot.setTitle(t("pie_title"), color="#7aa2ff", size="12pt")
        self.bar_plot.setLabel("left", "Watts", color="#8a93ad")
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
        self.hero_power.setText(f"{power_w:.0f} W")
        tdp = reg.total_tdp() or 1
        self.hero_bar.setValue(int(min(100, power_w / tdp * 100)))
        self.power_label.setText(t("power_label", w=power_w, tdp=reg.total_tdp()))
        # progress bars
        self.cpu_bar.setValue(int(snap.cpu.percent))
        self.cpu_lbl.setText(f"{snap.cpu.percent:.0f}%")
        self.ram_bar.setValue(int(snap.memory.percent))
        self.ram_lbl.setText(f"{snap.memory.percent:.0f}%")
        gpu_pct = (snap.gpus[0].load * 100) if snap.gpus else 0.0
        self.gpu_bar.setValue(int(gpu_pct))
        self.gpu_lbl.setText(f"{gpu_pct:.0f}%")
        # history
        self._power_history.append(power_w)
        self._cpu_history.append(snap.cpu.percent)
        self._gpu_history.append(gpu_pct)
        self.curve_power.setData(list(self._power_history))
        self.curve_cpu.setData(list(self._cpu_history))
        self.curve_gpu.setData(list(self._gpu_history))
        # bar chart
        names = [c.name[:14] for c in reg.components]
        vals = [c.current_watts for c in reg.components]
        colors = ["#4a6cf7"] * len(names)
        bg = pg.BarGraphItem(x=range(len(names)), height=vals, width=0.6, brushes=colors)
        self.bar_plot.clear()
        self.bar_plot.addItem(bg)
        ax = self.bar_plot.getAxis("bottom")
        ax.setTicks([[(i, n) for i, n in enumerate(names)]])

    def retranslate(self) -> None:
        metric_keys = ["metric_cpu_pct", "metric_cpu_temp", "metric_cpu_freq", "metric_ram_pct",
                      "metric_ram_used", "metric_disk_pct", "metric_disk_r", "metric_disk_w",
                      "metric_net_up", "metric_net_down", "metric_gpu_load", "metric_gpu_temp",
                      "metric_power", "metric_session_cost"]
        for k in metric_keys:
            if k in self.boxes:
                self.boxes[k].setTitle(t(k))
        self.plot.setTitle(t("chart_power"), color="#7aa2ff", size="12pt")
        self.bar_plot.setTitle(t("pie_title"), color="#7aa2ff", size="12pt")
