"""Main application window."""
from __future__ import annotations

import time

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QSystemTrayIcon,
    QMenu,
    QMainWindow,
    QStatusBar,
    QTabWidget,
)

from ..core.components import ComponentRegistry, build_default_registry
from ..core.monitor import SystemMonitor, SystemSnapshot
from ..core.power import Tariff, total_power_watts, update_registry_from_snapshot
from ..core.tracker import SessionTracker
from ..utils.i18n import set_language, t
from ..utils.styles import DARK_QSS
from PySide6.QtGui import QAction, QIcon, QKeySequence, QShortcut
from ..db.models import Base, SessionRecord, make_engine, make_session_factory
from ..db.repository import Repository
from ..utils.config import db_path
from .components_view import ComponentsView
from .dashboard import DashboardView
from .history_view import HistoryView
from .insights_view import InsightsView
from .settings_view import SettingsView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setStyleSheet(DARK_QSS)
        icon_path = __import__("pathlib").Path(__file__).resolve().parents[3] / "resources" / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.setWindowTitle(t("app_title"))
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
        lang = self.repo.get_setting("language", "en")
        set_language(lang or "en")

        self.tracker = SessionTracker()
        self.monitor = SystemMonitor(interval=1.0)

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
        self.insights_view = InsightsView(self)
        tabs.addTab(self.dashboard, "📊  " + t("tab_dashboard"))
        tabs.addTab(self.components_view, "🔧  " + t("tab_components"))
        tabs.addTab(self.history_view, "📜  " + t("tab_history"))
        tabs.addTab(self.settings_view, "⚙️  " + t("tab_settings"))
        tabs.addTab(self.insights_view, "💡  " + t("tab_insights"))
        self.setCentralWidget(tabs)
        for i in range(5):
            sc = QShortcut(QKeySequence(f"Ctrl+{i+1}"), self)
            sc.activated.connect(lambda idx=i: tabs.setCurrentIndex(idx))

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage(t("status_running"))

        # system tray
        self.tray = QSystemTrayIcon(self)
        icon_path = __import__('pathlib').Path(__file__).resolve().parents[3] / "resources" / "icon.ico"
        if icon_path.exists():
            self.tray.setIcon(QIcon(str(icon_path)))
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        self.tray.setContextMenu(tray_menu)
        self.tray.show()

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._collect_tick)
        self._timer.start()

    def _on_snapshot(self, snap) -> None:
        self._last_snapshot = snap
        update_registry_from_snapshot(self.registry, snap)
        self._last_power_watts = total_power_watts(self.registry)
        self.tracker.record(self._last_power_watts)
        try:
            self.dashboard.update_snapshot(snap, self._last_power_watts, self.registry)
        except Exception as e:
            import traceback; traceback.print_exc()

    def _collect_tick(self) -> None:
        try:
            snap = self.monitor.collect()
            self._on_snapshot(snap)
        except Exception as e:
            import traceback
            traceback.print_exc()
        self._tick()

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
        msg = t("status_power", w=self._last_power_watts, c=self.repo.total_cost(), cur=self.tariff.currency)
        try:
            thr = float(self.repo.get_setting("threshold", "300") or 300)
            if self._last_power_watts > thr:
                msg += "  |  ! " + t("threshold") + f" {thr:.0f}W"
        except Exception:
            pass
        self.status.showMessage(msg)
        try:
            self.tray.setToolTip(f"Rozetka - {self._last_power_watts:.0f} W")
        except Exception:
            pass

    def rebuild_ui(self) -> None:
        tabs = self.centralWidget()
        current = tabs.currentIndex() if tabs else 0
        # recreate views
        self.dashboard = DashboardView(self)
        self.components_view = ComponentsView(self)
        self.history_view = HistoryView(self)
        self.settings_view = SettingsView(self)
        self.insights_view = InsightsView(self)
        # rebuild tab widget
        new_tabs = QTabWidget()
        new_tabs.addTab(self.dashboard, "\U0001f4ca  " + t("tab_dashboard"))
        new_tabs.addTab(self.components_view, "\U0001f527  " + t("tab_components"))
        new_tabs.addTab(self.history_view, "\U0001f4dc  " + t("tab_history"))
        new_tabs.addTab(self.settings_view, "\u2699\ufe0f  " + t("tab_settings"))
        new_tabs.addTab(self.insights_view, "\U0001f4a1  " + t("tab_insights"))
        new_tabs.setCurrentIndex(current)
        self.setCentralWidget(new_tabs)
        self.retranslate()

    def retranslate(self) -> None:
        self.setWindowTitle(t("app_title"))
        tabs = self.centralWidget()
        tabs.setTabText(0, "📊  " + t("tab_dashboard"))
        tabs.setTabText(1, "🔧  " + t("tab_components"))
        tabs.setTabText(2, "📜  " + t("tab_history"))
        tabs.setTabText(3, "⚙️  " + t("tab_settings"))
        tabs.setTabText(4, "💡  " + t("tab_insights"))
        self.dashboard.retranslate()
        self.components_view.retranslate()
        self.history_view.retranslate()
        self.settings_view.retranslate()
        self.status.showMessage(t("status_running"))

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
        self.db_session.close()
        super().closeEvent(event)