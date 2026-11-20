"""Main application window."""
from __future__ import annotations

import time

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QTabWidget,
)

from ..core.components import ComponentRegistry, build_default_registry
from ..core.monitor import SystemMonitor, SystemSnapshot
from ..core.power import Tariff, total_power_watts, update_registry_from_snapshot
from ..core.tracker import SessionTracker
from ..db.models import Base, SessionRecord, make_engine, make_session_factory
from ..db.repository import Repository
from ..utils.config import db_path
from .components_view import ComponentsView
from .dashboard import DashboardView
from .history_view import HistoryView
from .settings_view import SettingsView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Rozetka - PC Power Tracker")
        self.resize(1100, 720)

        # Database
        self.engine = make_engine(str(db_path()))
        Base.metadata.create_all(self.engine)
        self.session_factory = make_session_factory(self.engine)
        self.db_session = self.session_factory()
        self.repo = Repository(self.db_session)

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

        self.tracker = SessionTracker()
        self.monitor = SystemMonitor(interval=1.0)
        self.monitor.subscribe(self._on_snapshot)
        self.monitor.start()

        self._last_snapshot = None
        self._last_power_watts = 0.0
        self._boot_recorded = False
        self._boot_start = time.time()
        self._boot_session_id = self.repo.create_session(is_boot=True).id
        self._current_session_id = self._boot_session_id
        self.tracker.start_session(is_boot=True)

        # UI
        tabs = QTabWidget()
        self.dashboard = DashboardView(self)
        self.components_view = ComponentsView(self)
        self.history_view = HistoryView(self)
        self.settings_view = SettingsView(self)
        tabs.addTab(self.dashboard, "Dashboard")
        tabs.addTab(self.components_view, "Components")
        tabs.addTab(self.history_view, "History")
        tabs.addTab(self.settings_view, "Settings")
        self.setCentralWidget(tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Running")

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _on_snapshot(self, snap) -> None:
        self._last_snapshot = snap
        update_registry_from_snapshot(self.registry, snap)
        self._last_power_watts = total_power_watts(self.registry)
        self.tracker.record(self._last_power_watts)
        try:
            self.dashboard.update_snapshot(snap, self._last_power_watts, self.registry)
        except Exception:
            pass

    def _tick(self) -> None:
        now = time.time()
        # finalize boot session after 60s, start normal session
        if not self._boot_recorded and now - self._boot_start >= 60:
            self._boot_recorded = True
            boot_sess = self.tracker.end_session()
            if boot_sess is not None and self._boot_session_id is not None:
                rec = self.db_session.query(SessionRecord).filter_by(id=self._boot_session_id).first()
                if rec is not None:
                    self.repo.close_session(
                        rec,
                        boot_sess.total_kwh(),
                        boot_sess.total_kwh() * self.tariff.price_per_kwh,
                        (sum(s.watts for s in boot_sess.samples) / len(boot_sess.samples)) if boot_sess.samples else 0.0,
                        boot_sess.duration_seconds(),
                    )
            self.tracker.start_session(is_boot=False)
            self._current_session_id = self.repo.create_session(is_boot=False).id

        self.components_view.refresh(self.registry)
        self.history_view.refresh(self.repo, self.tracker)
        self.status.showMessage(
            f"Power: {self._last_power_watts:.1f} W | Total cost: {self.repo.total_cost():.4f} {self.tariff.currency}"
        )

    def closeEvent(self, event) -> None:  # noqa: N802
        try:
            sess = self.tracker.end_session()
            if sess is not None and self._current_session_id is not None:
                rec = self.db_session.query(SessionRecord).filter_by(id=self._current_session_id).first()
                if rec is not None:
                    self.repo.close_session(
                        rec,
                        sess.total_kwh(),
                        sess.total_kwh() * self.tariff.price_per_kwh,
                        (sum(s.watts for s in sess.samples) / len(sess.samples)) if sess.samples else 0.0,
                        sess.duration_seconds(),
                    )
        except Exception:
            pass
        self.monitor.stop()
        self.db_session.close()
        super().closeEvent(event)