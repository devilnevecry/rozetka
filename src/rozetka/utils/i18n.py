"""Simple internationalization helper (RU/EN)."""
from __future__ import annotations

LANGUAGES = {
    "en": "English",
    "ru": "???????",
}

_TRANSLATIONS = {
    "en": {
        "app_title": "Rozetka - PC Power Tracker",
        "tab_dashboard": "Dashboard",
        "tab_components": "Components",
        "tab_history": "History",
        "tab_settings": "Settings",
        "metric_cpu_pct": "CPU %",
        "metric_cpu_temp": "CPU Temp",
        "metric_cpu_freq": "CPU Freq",
        "metric_ram_pct": "RAM %",
        "metric_ram_used": "RAM Used",
        "metric_disk_pct": "Disk %",
        "metric_disk_r": "Disk R",
        "metric_disk_w": "Disk W",
        "metric_net_up": "Net Up",
        "metric_net_down": "Net Down",
        "metric_gpu_load": "GPU Load",
        "metric_gpu_temp": "GPU Temp",
        "metric_power": "Power (W)",
        "metric_session_cost": "Session Cost",
        "power_label": "Power: {w:.1f} W  |  Total TDP: {tdp:.0f} W",
        "chart_power": "Power (W) over time",
        "btn_save_tdp": "Save TDP changes",
        "col_name": "Name",
        "col_category": "Category",
        "col_tdp": "TDP (W)",
        "col_load": "Load %",
        "col_current": "Current (W)",
        "total_cost": "Total cost: {v:.4f} {cur}",
        "total_kwh": "Total kWh: {v:.4f}",
        "col_id": "ID",
        "col_start": "Start",
        "col_end": "End",
        "col_boot": "Boot",
        "col_kwh": "kWh",
        "col_cost": "Cost",
        "running": "running",
        "yes": "yes",
        "no": "no",
        "btn_refresh": "Refresh",
        "lbl_tariff": "Price per kWh:",
        "lbl_currency": "Currency:",
        "lbl_language": "Language:",
        "btn_save": "Save",
        "status_running": "Running",
        "status_power": "Power: {w:.1f} W | Total cost: {c:.4f} {cur}",
    },
    "ru": {
        "app_title": "Rozetka - ???? ??????????? ??",
        "tab_dashboard": "??????",
        "tab_components": "??????????",
        "tab_history": "???????",
        "tab_settings": "?????????",
        "metric_cpu_pct": "???????? CPU %",
        "metric_cpu_temp": "????. CPU",
        "metric_cpu_freq": "??????? CPU",
        "metric_ram_pct": "???????? RAM %",
        "metric_ram_used": "???????????? RAM",
        "metric_disk_pct": "???????? ????? %",
        "metric_disk_r": "?????? ?????",
        "metric_disk_w": "?????? ?????",
        "metric_net_up": "?????? ????",
        "metric_net_down": "????? ????",
        "metric_gpu_load": "???????? GPU %",
        "metric_gpu_temp": "????. GPU",
        "metric_power": "???????? (??)",
        "metric_session_cost": "????????? ??????",
        "power_label": "????????: {w:.1f} ??  |  ????. TDP: {tdp:.0f} ??",
        "chart_power": "???????? (??) ?? ???????",
        "btn_save_tdp": "????????? TDP",
        "col_name": "???",
        "col_category": "?????????",
        "col_tdp": "TDP (??)",
        "col_load": "???????? %",
        "col_current": "??????? (??)",
        "total_cost": "????? ?????????: {v:.4f} {cur}",
        "total_kwh": "????? ?????: {v:.4f}",
        "col_id": "ID",
        "col_start": "??????",
        "col_end": "?????",
        "col_boot": "???????? ??",
        "col_kwh": "?????",
        "col_cost": "?????????",
        "running": "????????",
        "yes": "??",
        "no": "???",
        "btn_refresh": "????????",
        "lbl_tariff": "???? ?? ?????:",
        "lbl_currency": "??????:",
        "lbl_language": "????:",
        "btn_save": "?????????",
        "status_running": "????????",
        "status_power": "????????: {w:.1f} ?? | ?????: {c:.4f} {cur}",
    },
}

_current = "en"


def set_language(lang: str) -> None:
    global _current
    if lang in _TRANSLATIONS:
        _current = lang


def get_language() -> str:
    return _current


def t(key: str, **kwargs) -> str:
    val = _TRANSLATIONS.get(_current, _TRANSLATIONS["en"]).get(key)
    if val is None:
        val = _TRANSLATIONS["en"].get(key, key)
    if kwargs:
        try:
            return val.format(**kwargs)
        except Exception:
            return val
    return val
