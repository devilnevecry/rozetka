"""Dashboard view (CustomTkinter, lightweight canvas charts)."""
from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from ..utils.i18n import t


class DashboardView(ctk.CTkFrame):
    def __init__(self, main) -> None:
        super().__init__(main.content, fg_color="transparent")
        self.main = main
        self._power_history = []
        self._cpu_history = []
        self._gpu_history = []

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.hero_power = self._hero("Power", "0 W", "#2563eb")
        self.hero_cpu = self._hero("CPU", "0%", "#16a34a")
        self.hero_ram = self._hero("RAM", "0%", "#d97706")
        self.hero_gpu = self._hero("GPU", "0%", "#dc2626")
        for i, c in enumerate([self.hero_power, self.hero_cpu, self.hero_ram, self.hero_gpu]):
            c.grid(row=0, column=i, padx=6, pady=6, sticky="ew")

        self.labels = {}
        metric_keys = ["metric_cpu_pct", "metric_cpu_temp", "metric_cpu_freq", "metric_ram_pct",
                      "metric_ram_used", "metric_disk_pct", "metric_disk_r", "metric_disk_w",
                      "metric_net_up", "metric_net_down", "metric_gpu_load", "metric_gpu_temp",
                      "metric_power", "metric_session_cost"]
        for i, k in enumerate(metric_keys):
            card = ctk.CTkFrame(self, corner_radius=6)
            card.grid(row=1, column=i % 4, padx=6, pady=4, sticky="ew")
            ctk.CTkLabel(card, text=t(k), font=ctk.CTkFont(size=9, weight="bold"), text_color="#8a8f9e").pack(padx=8, pady=(6, 0))
            lbl = ctk.CTkLabel(card, text="0", font=ctk.CTkFont(size=14, weight="bold"))
            lbl.pack(padx=8, pady=(0, 6))
            self.labels[k] = lbl

        # Power chart canvas
        self.power_canvas = tk.Canvas(self, bg="#11141b", highlightthickness=0)
        self.power_canvas.grid(row=2, column=0, columnspan=4, padx=6, pady=6, sticky="nsew")
        self.power_canvas.bind("<Configure>", lambda e: self._draw_power_chart())

        # Bar chart canvas
        self.bar_canvas = tk.Canvas(self, bg="#11141b", highlightthickness=0)
        self.bar_canvas.grid(row=3, column=0, columnspan=4, padx=6, pady=6, sticky="nsew")
        self.bar_canvas.bind("<Configure>", lambda e: self._draw_bar_chart())

        self.power_label = ctk.CTkLabel(self, text="", text_color="#8a8f9e", font=ctk.CTkFont(size=9))
        self.power_label.grid(row=4, column=0, columnspan=4, padx=6, pady=4)

        self._last_reg = None

    def _hero(self, title, value, color):
        card = ctk.CTkFrame(self, corner_radius=6)
        ctk.CTkLabel(card, text=title, text_color="#8a8f9e", font=ctk.CTkFont(size=9, weight="bold")).pack(padx=12, pady=(8, 0))
        lbl = ctk.CTkLabel(card, text=value, text_color=color, font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(padx=12, pady=(0, 8))
        setattr(self, f"hero_{title.lower()}_lbl", lbl)
        return card

    def update_snapshot(self, snap, power_w, reg) -> None:
        self.labels["metric_cpu_pct"].configure(text=f"{snap.cpu.percent:.1f}")
        self.labels["metric_cpu_temp"].configure(text=f"{snap.cpu.temp_c:.1f} C" if snap.cpu.temp_c is not None else "n/a")
        self.labels["metric_cpu_freq"].configure(text=f"{snap.cpu.freq_mhz:.0f} MHz")
        self.labels["metric_ram_pct"].configure(text=f"{snap.memory.percent:.1f}")
        self.labels["metric_ram_used"].configure(text=f"{snap.memory.used_gb:.2f} GB")
        self.labels["metric_disk_pct"].configure(text=f"{snap.disk.percent:.1f}")
        self.labels["metric_disk_r"].configure(text=f"{snap.disk.read_bytes_s/1024:.1f} KB/s")
        self.labels["metric_disk_w"].configure(text=f"{snap.disk.write_bytes_s/1024:.1f} KB/s")
        self.labels["metric_net_up"].configure(text=f"{snap.net.sent_bytes_s/1024:.1f} KB/s")
        self.labels["metric_net_down"].configure(text=f"{snap.net.recv_bytes_s/1024:.1f} KB/s")
        if snap.gpus:
            g = snap.gpus[0]
            self.labels["metric_gpu_load"].configure(text=f"{g.load*100:.1f}")
            self.labels["metric_gpu_temp"].configure(text=f"{g.temp_c:.1f} C" if g.temp_c is not None else "n/a")
        else:
            self.labels["metric_gpu_load"].configure(text="n/a")
            self.labels["metric_gpu_temp"].configure(text="n/a")
        self.labels["metric_power"].configure(text=f"{power_w:.1f}")
        try:
            sess = self.main.tracker.current
            if sess is not None:
                kwh = sess.total_kwh()
                cost = kwh * self.main.tariff.price_per_kwh
                self.labels["metric_session_cost"].configure(text=f"{cost:.4f}")
        except Exception:
            pass

        self.hero_power_lbl.configure(text=f"{power_w:.0f} W")
        self.hero_cpu_lbl.configure(text=f"{snap.cpu.percent:.0f}%")
        self.hero_ram_lbl.configure(text=f"{snap.memory.percent:.0f}%")
        gpu_pct = (snap.gpus[0].load * 100) if snap.gpus else 0.0
        self.hero_gpu_lbl.configure(text=f"{gpu_pct:.0f}%")

        self.power_label.configure(text=t("power_label", w=power_w, tdp=reg.total_tdp()))

        self._power_history.append(power_w)
        self._cpu_history.append(snap.cpu.percent)
        self._gpu_history.append(gpu_pct)
        if len(self._power_history) > 180:
            self._power_history.pop(0)
            self._cpu_history.pop(0)
            self._gpu_history.pop(0)
        self._last_reg = reg
        self._draw_power_chart()
        self._draw_bar_chart()

    def _draw_power_chart(self) -> None:
        c = self.power_canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10 or h < 10:
            return
        pad = 20
        # axes
        c.create_line(pad, pad, pad, h - pad, fill="#1f2330")
        c.create_line(pad, h - pad, w - pad, h - pad, fill="#1f2330")
        data = self._power_history
        if not data:
            return
        mn = min(data)
        mx = max(data) or 1
        rng = mx - mn or 1
        n = len(data)
        pts_power = []
        pts_cpu = []
        pts_gpu = []
        for i, (pw, cpu, gpu) in enumerate(zip(data, self._cpu_history, self._gpu_history)):
            x = pad + (w - 2 * pad) * i / max(n - 1, 1)
            y_pw = h - pad - (h - 2 * pad) * (pw - mn) / rng
            y_cpu = h - pad - (h - 2 * pad) * (cpu / 100.0)
            y_gpu = h - pad - (h - 2 * pad) * (gpu / 100.0)
            pts_power.append((x, y_pw))
            pts_cpu.append((x, y_cpu))
            pts_gpu.append((x, y_gpu))
        for pts, color in (pts_power, "#2563eb"), (pts_cpu, "#16a34a"), (pts_gpu, "#dc2626"):
            for i in range(1, len(pts)):
                c.create_line(pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1], fill=color, width=2)

    def _draw_bar_chart(self) -> None:
        c = self.bar_canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10 or h < 10 or self._last_reg is None:
            return
        reg = self._last_reg
        names = [x.name[:12] for x in reg.components]
        vals = [x.current_watts for x in reg.components]
        if not vals:
            return
        mx = max(vals) or 1
        pad = 20
        n = len(vals)
        bar_w = (w - 2 * pad) / max(n, 1) * 0.6
        for i, (name, v) in enumerate(zip(names, vals)):
            x = pad + (w - 2 * pad) * (i + 0.5) / n
            bar_h = (h - 2 * pad) * (v / mx)
            c.create_rectangle(x - bar_w/2, h - pad - bar_h, x + bar_w/2, h - pad, fill="#2563eb", outline="")
            c.create_text(x, h - pad + 12, text=name, fill="#8a8f9e", font=("Segoe UI", 8))
            c.create_text(x, h - pad - bar_h - 8, text=f"{v:.0f}", fill="#8a8f9e", font=("Segoe UI", 8))

    def retranslate(self) -> None:
        pass
