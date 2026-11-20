"""Main application window (CustomTkinter)."""
from __future__ import annotations

import time

import customtkinter as ctk

from ..core.components import build_default_registry
from ..core.monitor import SystemMonitor
from ..core.power import Tariff, total_power_watts, update_registry_from_snapshot
from ..core.tracker import SessionTracker
from ..db import Repository
from ..utils.autostart import disable as disable_autostart, enable as enable_autostart, is_enabled
from ..utils.config import db_path
from ..utils.i18n import LANGUAGES, get_language, set_language, t
from .dashboard import DashboardView
from .components_view import ComponentsView
from .history_view import HistoryView
from .settings_view import SettingsView
from .insights_view import InsightsView


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(t("app_title"))
        self.geometry("1200x760")
        self.minsize(900, 600)

        # Database
        self.repo = Repository(db_path())

        # Core
        self.registry = build_default_registry()
        for cfg in self.repo.list_components():
            for c in self.registry.components:
                if c.name == cfg.name:
                    c.tdp_watts = cfg.tdp_watts
                    c.idle_watts = cfg.idle_watts
        for c in self.registry.components:
            self.repo.upsert_component(c.name, c.category.value, c.tdp_watts, c.idle_watts)

        tariff_val = self.repo.get_setting("tariff", "5.0")
        self.tariff = Tariff(price_per_kwh=float(tariff_val) if tariff_val else 5.0)
        cur = self.repo.get_setting("currency")
        if cur:
            self.tariff.currency = cur
        lang = self.repo.get_setting("language", "en")
        set_language(lang or "en")

        self.tracker = SessionTracker()
        self.monitor = SystemMonitor(interval=1.0)

        self._last_power_watts = 0.0
        self._boot_start = time.time()
        self._boot_session_id = self.repo.create_session(is_boot=True)
        self._current_session_id = self._boot_session_id
        self.tracker.start_session(is_boot=True)

        # Layout: sidebar + content
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # Views
        self.dashboard = DashboardView(self)
        self.components_view = ComponentsView(self)
        self.history_view = HistoryView(self)
        self.settings_view = SettingsView(self)
        self.insights_view = InsightsView(self)

        self.views = [self.dashboard, self.components_view, self.history_view, self.settings_view, self.insights_view]
        self.view_names = [t("tab_dashboard"), t("tab_components"), t("tab_history"), t("tab_settings"), t("tab_insights")]
        self.view_icons = ["\U0001f4ca", "\U0001f527", "\U0001f4dc", "\u2699\ufe0f", "\U0001f4a1"]

        self.current_view = None
        self._build_sidebar()
        self.show_view(0)

        # Status bar
        self.status = ctk.CTkLabel(self, text=t("status_running"), anchor="w")
        self.status.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=4)

        # Timer
        self._timer = None
        self._start_timer()

    def _build_sidebar(self) -> None:
        ctk.CTkLabel(self.sidebar, text="Rozetka", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, padx=16, pady=(16, 8))
        for i, (name, icon) in enumerate(zip(self.view_names, self.view_icons)):
            btn = ctk.CTkButton(self.sidebar, text=f"{icon}  {name}", anchor="w",
                                fg_color="transparent", hover_color=("#2a3148", "#2a3148"),
                                command=lambda idx=i: self.show_view(idx))
            btn.grid(row=i + 1, column=0, padx=8, pady=4, sticky="ew")
        # power label at bottom
        self.sidebar_power = ctk.CTkLabel(self.sidebar, text="0 W", font=ctk.CTkFont(size=14, weight="bold"))
        self.sidebar_power.grid(row=7, column=0, padx=16, pady=16)

    def show_view(self, idx: int) -> None:
        if self.current_view is not None:
            self.current_view.grid_forget()
        self.current_view = self.views[idx]
        self.current_view.grid(row=0, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def _start_timer(self) -> None:
        self._timer = self.after(1000, self._collect_tick)

    def _collect_tick(self) -> None:
        try:
            snap = self.monitor.collect()
            self._on_snapshot(snap)
        except Exception as e:
            print("collect error:", e)
        self._tick()
        self._timer = self.after(1000, self._collect_tick)

    def _on_snapshot(self, snap) -> None:
        update_registry_from_snapshot(self.registry, snap)
        self._last_power_watts = total_power_watts(self.registry)
        self.tracker.record(self._last_power_watts)
        try:
            self.dashboard.update_snapshot(snap, self._last_power_watts, self.registry)
        except Exception:
            pass

    def _tick(self) -> None:
        now = __import__("time").time()
        # boot session finalize after 60s
        if not hasattr(self, "_boot_recorded"):
            self._boot_recorded = False
            self._boot_start = __import__("time").time()
        if not self._boot_recorded and now - self._boot_start >= 60:
            self._boot_recorded = True
            boot_sess = self.tracker.end_session()
            if boot_sess is not None and self._boot_session_id is not None:
                self.repo.close_session(self._boot_session_id, boot_sess.total_kwh(),
                                           boot_sess.total_kwh() * self.tariff.price_per_kwh,
                                           (sum(s.watts for s in boot_sess.samples) / len(boot_sess.samples)) if boot_sess.samples else 0.0,
                                           boot_sess.duration_seconds())
            self.tracker.start_session(is_boot=False)
            self._current_session_id = self.repo.create_session(is_boot=False)
        try:
            self.components_view.refresh(self.registry)
            self.history_view.refresh(self.repo, self.tracker)
            self.insights_view.refresh()
        except Exception:
            pass
        self.status.configure(text=t("status_power", w=self._last_power_watts, c=self.repo.total_cost(), cur=self.tariff.currency))
        self.sidebar_power.configure(text=f"{self._last_power_watts:.0f} W")

    def rebuild_ui(self) -> None:
        # reload language and recreate views
        lang = self.repo.get_setting("language", "en")
        set_language(lang or "en")
        # recreate views
        self.dashboard.destroy()
        self.components_view.destroy()
        self.history_view.destroy()
        self.settings_view.destroy()
        self.insights_view.destroy()
        self.dashboard = DashboardView(self)
        self.components_view = ComponentsView(self)
        self.history_view = HistoryView(self)
        self.settings_view = SettingsView(self)
        self.insights_view = InsightsView(self)
        self.views = [self.dashboard, self.components_view, self.history_view, self.settings_view, self.insights_view]
        self.view_names = [t("tab_dashboard"), t("tab_components"), t("tab_history"), t("tab_settings"), t("tab_insights")]
        # rebuild sidebar labels
        for w in self.sidebar.winfo_children():
            w.destroy()
        self._build_sidebar()
        self.show_view(0)

    def on_close(self) -> None:
        try:
            sess = self.tracker.end_session()
            if sess is not None and self._current_session_id is not None:
                self.repo.close_session(self._current_session_id, sess.total_kwh(),
                                           sess.total_kwh() * self.tariff.price_per_kwh,
                                           (sum(s.watts for s in sess.samples) / len(sess.samples)) if sess.samples else 0.0,
                                           sess.duration_seconds())
        except Exception:
            pass
        self.destroy()
