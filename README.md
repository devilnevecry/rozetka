# Rozetka

Cross-platform desktop application for tracking PC power consumption, per-component
resource usage and cost accounting.

## Features

- Real-time monitoring of CPU, GPU, RAM, disks, network, temperatures
- Per-component power estimation (TDP x load) with user-editable TDP values
- Session cost calculation based on configurable electricity tariff
- Boot cost accounting (energy during OS startup)
- Persistent history (SQLite)
- Per-component breakdown

## Stack

- Python 3.11+, PySide6 (Qt), psutil, SQLAlchemy

## Run

`ash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m rozetka.main
`

## License

MIT
