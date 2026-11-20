# Rozetka

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Cross-platform desktop application for tracking PC power consumption, per-component
resource usage and cost accounting.

## Features

- Real-time monitoring of CPU, GPU, RAM, disks, network and temperatures
- Per-component power estimation (TDP x load) with user-editable TDP values
- Session and boot cost calculation based on a configurable electricity tariff
- Persistent history with totals (SQLite)
- Per-component breakdown and live power chart

## Stack

- Python 3.11+, PySide6 (Qt), psutil, SQLAlchemy, pyqtgraph

## Install and run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m rozetka.main
```

## Tests

```bash
pip install pytest
python -m pytest -q
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Build .exe

```powershell
.\scripts\build.ps1
```

Produces `dist/Rozetka/Rozetka.exe`.

## License

MIT
