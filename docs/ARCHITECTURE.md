# Architecture

Rozetka is a desktop application built with PySide6.

## Modules

- `core/monitor.py` - system metrics via psutil (+ optional NVML for NVIDIA GPU).
- `core/components.py` - component registry with TDP and load estimation.
- `core/power.py` - power/cost calculations.
- `core/tracker.py` - session tracking and energy integration.
- `db/` - SQLAlchemy models and repository (SQLite).
- `ui/` - PySide6 views.
- `utils/config.py` - paths and JSON helpers.

## Data flow

Monitor collects a `SystemSnapshot` each second, updates component loads in the
registry, computes total watts, records a sample into the current session, and
refreshes the UI. Sessions are persisted to SQLite on close.
