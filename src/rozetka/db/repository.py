"""Data access layer."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from .models import ComponentConfig, SessionRecord, Settings


class Repository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # sessions
    def create_session(self, is_boot: bool = False) -> SessionRecord:
        rec = SessionRecord(start_ts=datetime.now(timezone.utc).replace(tzinfo=None), is_boot=1 if is_boot else 0)
        self.session.add(rec)
        self.session.commit()
        self.session.refresh(rec)
        return rec

    def close_session(self, rec: SessionRecord, energy_kwh: float, cost: float,
                      avg_watts: float, duration_s: float) -> None:
        rec.end_ts = datetime.now(timezone.utc).replace(tzinfo=None)
        rec.energy_kwh = energy_kwh
        rec.cost = cost
        rec.avg_watts = avg_watts
        rec.duration_s = duration_s
        self.session.commit()

    def list_sessions(self, limit: int = 200) -> List[SessionRecord]:
        return (self.session.query(SessionRecord)
                .order_by(SessionRecord.start_ts.desc())
                .limit(limit).all())

    def total_cost(self) -> float:
        rows = self.session.query(SessionRecord).all()
        return sum(r.cost or 0.0 for r in rows)

    def total_kwh(self) -> float:
        rows = self.session.query(SessionRecord).all()
        return sum(r.energy_kwh or 0.0 for r in rows)

    # component configs
    def upsert_component(self, name: str, category: str, tdp: float, idle: float) -> None:
        rec = self.session.query(ComponentConfig).filter_by(name=name).first()
        if rec is None:
            rec = ComponentConfig(name=name, category=category, tdp_watts=tdp, idle_watts=idle)
            self.session.add(rec)
        else:
            rec.category = category
            rec.tdp_watts = tdp
            rec.idle_watts = idle
        self.session.commit()

    def list_components(self) -> List[ComponentConfig]:
        return self.session.query(ComponentConfig).order_by(ComponentConfig.category).all()

    # settings
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        rec = self.session.query(Settings).filter_by(key=key).first()
        return rec.value if rec else default

    def set_setting(self, key: str, value: str) -> None:
        rec = self.session.query(Settings).filter_by(key=key).first()
        if rec is None:
            rec = Settings(key=key, value=value)
            self.session.add(rec)
        else:
            rec.value = value
        self.session.commit()