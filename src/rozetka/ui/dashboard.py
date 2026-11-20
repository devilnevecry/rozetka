"""Dashboard view with live metrics and charts."""
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
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Hero row: 4 large metric cards
        hero = QHBoxLayout()
        hero.setSpacing(12)
        self.hero_power = self._hero_card("Power", "0 W", "#2563eb")
        self.hero_cpu = self._hero_card("CPU", "0%", "#16a34a")
        self.hero_ram = self._hero_card("RAM", "0%", "#d97706")
        self.hero_gpu = self._hero_card("GPU", "0%", "#dc2626")
        for c in (self.hero_power, self.hero_cpu, self.hero_ram, self.hero_gpu):
            hero.addWidget(c)
        layout.addLayout(hero)

        # Progress bars
        pb = QHBoxLayout()
        pb.setSpacing(12)
        self.cpu_bar = self._progress_card("CPU", "#16a34a")
        self.ram_bar = self._progress_card("RAM", "#d97706")
        self.gpu_bar = self._progress_card("GPU", "#dc2626")
        for c in (self.cpu_bar, self.ram_bar, self.gpu_bar):
            pb.addWidget(c[0])
        layout.addLayout(pb)

        # Metric cards grid
        grid = QGridLayout()
        grid.setSpacing(8)
        self.labels = {}
        self.boxes = {}
        metric_keys = ["metric_cpu_pct", "metric_cpu_temp", "metric_cpu_freq", "metric_ram_pct",
                      "metric_ram_used", "metric_disk_pct", "metric_disk_r", "metric_disk_w",
                      "metric_net_up", "metric_net_down", "metric_gpu_load", "metric_gpu_temp",
                      "metric_power", "metric_session_cost"]
        row = 0
        col = 0
        for k in metric_keys:
            box = QGroupBox(t(k))
            lbl = QLabel("0")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 13pt; font-weight: 600;")
            v = QVBoxLayout()
            v.setContentsMargins(8, 8, 8, 8)
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

        # Power chart
        self.plot = pg.PlotWidget()
        self.plot.setBackground("#11141b")
        self.plot.setTitle(t("chart_power"), color="#8a8f9e", size="10pt")
        self.plot.setLabel("left", "Value", color="#8a8f9e")
        self.plot.setLabel("bottom", "Samples", color="#8a8f9e")
        self.plot.addLegend(offset=(10, 10))
        self.plot.showGrid(x=True, y=True, alpha=0.08)
        self.curve_power = self.plot.plot(pen=pg.mkPen("#2563eb", width=2), name="Power (W)")
        self.curve_cpu = self.plot.plot(pen=pg.mkPen("#16a34a", width=1.5), name="CPU %")
        self.curve_gpu = self.plot.plot(pen=pg.mkPen("#dc2626", width=1.5), name="GPU %")
        layout.addWidget(self.plot, stretch=2)

        # Component bar chart
        self.bar_plot = pg.PlotWidget()
        self.bar_plot.setBackground("#11141b")
        self.bar_plot.setTitle(t("pie_title"), color="#8a8f9e", size="10pt")
        self.bar_plot.setLabel("left", "Watts", color="#8a8f9e")
        self.bar_plot.showGrid(y=True, alpha=0.08)
        layout.addWidget(self.bar_plot, stretch=1)

        self.power_label = QLabel("")
        self.power_label.setStyleSheet("color: #8a8f9e; font-size: 9pt;")
        layout.addWidget(self.power_label)

    def _hero_card(self, title, value, color):
        box = QGroupBox(title)
        v = QVBoxLayout()
        v.setContentsMargins(12, 8, 12, 8)
        lbl = QLabel(value)
        lbl.setStyleSheet(f"font-size: 20pt; font-weight: 700; color: {color};")
        lbl.setAlignment(Qt.AlignCenter)
        v.addWidget(lbl)
        box.setLayout(v)
        setattr(self, f"hero_{title.lower()}_lbl", lbl)
        return box

    def _progress_card(self, title, color):
        box = QGroupBox(title)
        v = QVBoxLayout()
        v.setContentsMargins(12, 8, 12, 8)
        bar = QProgressBar()
        bar.setStyleSheet(f"QProgressBar::chunk {{ background: {color}; }}")
        v.addWidget(bar)
        lbl = QLabel("0%")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 9pt; color: #8a8f9e;")
        v.addWidget(lbl)
        box.setLayout(v)
        return (box, bar, lbl)

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

        self.hero_power_lbl.setText(f"{power_w:.0f} W")
        self.hero_cpu_lbl.setText(f"{snap.cpu.percent:.0f}%")
        self.hero_ram_lbl.setText(f"{snap.memory.percent:.0f}%")
        gpu_pct = (snap.gpus[0].load * 100) if snap.gpus else 0.0
        self.hero_gpu_lbl.setText(f"{gpu_pct:.0f}%")

        # progress bars: cpu_bar is tuple (box, bar, lbl)
        self.cpu_bar[1].setValue(int(snap.cpu.percent))
        self.cpu_bar[2].setText(f"{snap.cpu.percent:.0f}%")
        self.ram_bar[1].setValue(int(snap.memory.percent))
        self.ram_bar[2].setText(f"{snap.memory.percent:.0f}%")
        self.gpu_bar[1].setValue(int(gpu_pct))
        self.gpu_bar[2].setText(f"{gpu_pct:.0f}%")

        self.power_label.setText(t("power_label", w=power_w, tdp=reg.total_tdp()))
        self._power_history.append(power_w)
        self._cpu_history.append(snap.cpu.percent)
        self._gpu_history.append(gpu_pct)
        self.curve_power.setData(list(self._power_history))
        self.curve_cpu.setData(list(self._cpu_history))
        self.curve_gpu.setData(list(self._gpu_history))
        names = [c.name[:14] for c in reg.components]
        vals = [c.current_watts for c in reg.components]
        bg = pg.BarGraphItem(x=range(len(names)), height=vals, width=0.6, brushes="#2563eb")
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
        self.plot.setTitle(t("chart_power"), color="#8a8f9e", size="10pt")
        self.bar_plot.setTitle(t("pie_title"), color="#8a8f9e", size="10pt")
