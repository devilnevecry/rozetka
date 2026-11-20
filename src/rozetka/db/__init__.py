"""Lightweight SQLite persistence (no SQLAlchemy)."""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import List, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_ts REAL NOT NULL,
    end_ts REAL,
    is_boot INTEGER DEFAULT 0,
    energy_kwh REAL DEFAULT 0.0,
    cost REAL DEFAULT 0.0,
    avg_watts REAL DEFAULT 0.0,
    duration_s REAL DEFAULT 0.0
);
CREATE TABLE IF NOT EXISTS component_configs (
    name TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    tdp_watts REAL DEFAULT 0.0,
    idle_watts REAL DEFAULT 0.0
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


class Repository:
    def __init__(self, db_path: Path) -> None:
        self.conn = sqlite3.connect(str(db_path))
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # sessions
    def create_session(self, is_boot: bool = False) -> int:
        cur = self.conn.execute("INSERT INTO sessions (start_ts, is_boot) VALUES (?, ?)", (time.time(), 1 if is_boot else 0))
        self.conn.commit()
        return cur.lastrowid

    def close_session(self, sid: int, energy_kwh: float, cost: float, avg_watts: float, duration_s: float) -> None:
        self.conn.execute("UPDATE sessions SET end_ts=?, energy_kwh=?, cost=?, avg_watts=?, duration_s=? WHERE id=?",
                          (time.time(), energy_kwh, cost, avg_watts, duration_s, sid))
        self.conn.commit()

    def list_sessions(self, limit: int = 200):
        cur = self.conn.execute("SELECT id, start_ts, end_ts, is_boot, energy_kwh, cost, avg_watts, duration_s FROM sessions ORDER BY start_ts DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        # return simple objects
        out = []
        for r in rows:
            o = type("SessionRecord", (), {})()
            o.id, o.start_ts, o.end_ts, o.is_boot, o.energy_kwh, o.cost, o.avg_watts, o.duration_s = r
            o.is_boot = bool(o.is_boot)
            out.append(o)
        return out

    def total_cost(self) -> float:
        cur = self.conn.execute("SELECT COALESCE(SUM(cost),0) FROM sessions")
        return cur.fetchone()[0] or 0.0

    def total_kwh(self) -> float:
        cur = self.conn.execute("SELECT COALESCE(SUM(energy_kwh),0) FROM sessions")
        return cur.fetchone()[0] or 0.0

    # component configs
    def upsert_component(self, name: str, category: str, tdp: float, idle: float) -> None:
        self.conn.execute("INSERT INTO component_configs (name, category, tdp_watts, idle_watts) VALUES (?,?,?,?) "
                          "ON CONFLICT(name) DO UPDATE SET category=excluded.category, tdp_watts=excluded.tdp_watts, idle_watts=excluded.idle_watts",
                          (name, category, tdp, idle))
        self.conn.commit()

    def list_components(self):
        cur = self.conn.execute("SELECT name, category, tdp_watts, idle_watts FROM component_configs")
        out = []
        for r in cur.fetchall():
            o = type("ComponentConfig", (), {})()
            o.name, o.category, o.tdp_watts, o.idle_watts = r
            out.append(o)
        return out

    # settings
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        cur = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else default

    def set_setting(self, key: str, value: str) -> None:
        self.conn.execute("INSERT INTO settings (key, value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
        self.conn.commit()
