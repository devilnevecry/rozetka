"""Tests for repository layer."""
import tempfile
from pathlib import Path

from rozetka.db import Repository


def test_session_lifecycle():
    with tempfile.TemporaryDirectory() as d:
        repo = Repository(Path(d) / "t.db")
        sid = repo.create_session(is_boot=True)
        assert sid is not None
        repo.close_session(sid, 0.5, 2.5, 100.0, 1800.0)
        sessions = repo.list_sessions()
        assert len(sessions) == 1
        assert sessions[0].energy_kwh == 0.5
        assert repo.total_cost() == 2.5
        assert repo.total_kwh() == 0.5
        repo.close()


def test_component_upsert():
    with tempfile.TemporaryDirectory() as d:
        repo = Repository(Path(d) / "t.db")
        repo.upsert_component("CPU", "cpu", 65.0, 10.0)
        repo.upsert_component("CPU", "cpu", 80.0, 12.0)
        comps = repo.list_components()
        assert len(comps) == 1
        assert comps[0].tdp_watts == 80.0
        repo.close()


def test_settings():
    with tempfile.TemporaryDirectory() as d:
        repo = Repository(Path(d) / "t.db")
        repo.set_setting("tariff", "7.5")
        assert repo.get_setting("tariff") == "7.5"
        assert repo.get_setting("missing", "x") == "x"
        repo.close()
