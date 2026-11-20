"""SQLAlchemy models for persistent accounting."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


class SessionRecord(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_ts = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_ts = Column(DateTime, nullable=True)
    is_boot = Column(Integer, default=0)
    energy_kwh = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
    avg_watts = Column(Float, default=0.0)
    duration_s = Column(Float, default=0.0)


class SampleRecord(Base):
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, nullable=False)
    ts = Column(DateTime, nullable=False, default=datetime.utcnow)
    watts = Column(Float, default=0.0)
    cpu_percent = Column(Float, default=0.0)
    gpu_load = Column(Float, default=0.0)
    ram_percent = Column(Float, default=0.0)


class ComponentConfig(Base):
    __tablename__ = "component_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, unique=True)
    category = Column(String(32), nullable=False)
    tdp_watts = Column(Float, default=0.0)
    idle_watts = Column(Float, default=0.0)


class Settings(Base):
    __tablename__ = "settings"

    key = Column(String(64), primary_key=True)
    value = Column(Text, nullable=False)


def make_engine(db_path: str):
    return create_engine(f"sqlite:///{db_path}", echo=False, future=True)


def make_session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)