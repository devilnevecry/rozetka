
"""Dashboard view with live metrics and power chart."""
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


class DashboardView(QWidget):
    def __init__(self, main) -> None:
        super().__init__()
        self.main = main
        self._power_history = deque(maxlen=120)
        layout = QVBoxLayout(self)

        grid = QGridLayout()
        self.labels = {}
        metrics = ["CPU %", "CPU Temp", "CPU Freq", "RAM %", "RAM Used", "Disk %",
                   "Disk R", "Disk W", "Net Up", "Net Down", "GPU Load", "GPU Temp",
                   "Power (W)", "Session Cost"]
        row = 0
        col = 0
        for m in metrics:
            box = QGroupBox(m)
            lbl = QLabel("0")
            lbl.setAlignment(Qt.AlignCenter)
            v = QVBoxLayout()
            v.addWidget(lbl)
            box.setLayout(v)
            grid.addWidget(box, row, col)
            self.labels[m] = lbl
            col += 1
            if col >= 4:
                col = 0
                row += 1
        layout.addLayout(grid)

        self.power_label = QLabel("Power: 0 W")
        layout.addWidget(self.power_label)

        # chart
        self.plot = pg.PlotWidget()
        self.plot.setBackground("w")
        self.plot.setTitle("Power (W) over time")
        self.plot.setLabel("left", "Watts")
        self.plot.setLabel("bottom", "Samples")
        self.curve = self.plot.plot(pen=pg.mkPen("b", width=2))
        layout.addWidget(self.plot)

    def update_snapshot(self, snap: SystemSnapshot, power_w: float, reg: ComponentRegistry) -> None:
        self.labels["CPU %"].setText(f"{snap.cpu.percent:.1f}")
        self.labels["CPU Temp"].setText(f"{snap.cpu.temp_c:.1f} C" if snap.cpu.temp_c is not None else "n/a")
        self.labels["CPU Freq"].setText(f"{snap.cpu.freq_mhz:.0f} MHz")
        self.labels["RAM %"].setText(f"{snap.memory.percent:.1f}")
        self.labels["RAM Used"].setText(f"{snap.memory.used_gb:.2f} GB")
        self.labels["Disk %"].setText(f"{snap.disk.percent:.1f}")
        self.labels["Disk R"].setText(f"{snap.disk.read_bytes_s/1024:.1f} KB/s")
        self.labels["Disk W"].setText(f"{snap.disk.write_bytes_s/1024:.1f} KB/s")
        self.labels["Net Up"].setText(f"{snap.net.sent_bytes_s/1024:.1f} KB/s")
        self.labels["Net Down"].setText(f"{snap.net.recv_bytes_s/1024:.1f} KB/s")
        if snap.gpus:
            g = snap.gpus[0]
            self.labels["GPU Load"].setText(f"{g.load*100:.1f}")
            self.labels["GPU Temp"].setText(f"{g.temp_c:.1f} C" if g.temp_c is not None else "n/a")
        else:
            self.labels["GPU Load"].setText("n/a")
            self.labels["GPU Temp"].setText("n/a")
        self.labels["Power (W)"].setText(f"{power_w:.1f}")
        try:
            sess = self.main.tracker.current
            if sess is not None:
                kwh = sess.total_kwh()
                cost = kwh * self.main.tariff.price_per_kwh
                self.labels["Session Cost"].setText(f"{cost:.4f}")
        except Exception:
            pass
        self.power_label.setText(f"Power: {power_w:.1f} W  |  Total TDP: {reg.total_tdp():.0f} W")
        self._power_history.append(power_w)
        self.curve.setData(list(self._power_history))
