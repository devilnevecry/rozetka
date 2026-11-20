
"""Tests for repository layer."""
import tempfile
from pathlib import Path

from rozetka.db.models import Base, make_engine, make_session_factory
from rozetka.db.repository import Repository


def test_session_lifecycle():
    with tempfile.TemporaryDirectory() as d:
        engine = make_engine(str(Path(d) / "t.db"))
        Base.metadata.create_all(engine)
        sf = make_session_factory(engine)
        s = sf()
        repo = Repository(s)
        rec = repo.create_session(is_boot=True)
        assert rec.id is not None
        repo.close_session(rec, 0.5, 2.5, 100.0, 1800.0)
        sessions = repo.list_sessions()
        assert len(sessions) == 1
        assert sessions[0].energy_kwh == 0.5
        assert repo.total_cost() == 2.5
        assert repo.total_kwh() == 0.5
        s.close()
        engine.dispose()


def test_component_upsert():
    with tempfile.TemporaryDirectory() as d:
        engine = make_engine(str(Path(d) / "t.db"))
        Base.metadata.create_all(engine)
        sf = make_session_factory(engine)
        s = sf()
        repo = Repository(s)
        repo.upsert_component("CPU", "cpu", 65.0, 10.0)
        repo.upsert_component("CPU", "cpu", 80.0, 12.0)
        comps = repo.list_components()
        assert len(comps) == 1
        assert comps[0].tdp_watts == 80.0
        s.close()
        engine.dispose()


def test_settings():
    with tempfile.TemporaryDirectory() as d:
        engine = make_engine(str(Path(d) / "t.db"))
        Base.metadata.create_all(engine)
        sf = make_session_factory(engine)
        s = sf()
        repo = Repository(s)
        repo.set_setting("tariff", "7.5")
        assert repo.get_setting("tariff") == "7.5"
        assert repo.get_setting("missing", "x") == "x"
        s.close()
        engine.dispose()
