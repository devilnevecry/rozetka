"""Simple internationalization helper (RU/EN)."""
from __future__ import annotations

LANGUAGES = {
    "en": "English",
    "ru": "\u0420\u0443\u0441\u0441\u043a\u0438\u0439",
}

_TRANSLATIONS = {
    "en": {
        "app_title": "Rozetka - PC Power Tracker",
        "tab_dashboard": "Dashboard",
        "tab_components": "Components",
        "tab_history": "History",
        "tab_settings": "Settings",
        "tab_insights": "Insights",
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
        "export_csv": "Export CSV",
        "recommendations": "Recommendations",
        "threshold": "Power threshold (W):",
    },
    "ru": {
        "app_title": "\u0420\u043e\u0437\u0435\u0442\u043a\u0430 \u2014 \u0443\u0447\u0451\u0442 \u043f\u043e\u0442\u0440\u0435\u0431\u043b\u0435\u043d\u0438\u044f \u041f\u041a",
        "tab_dashboard": "\u041f\u0430\u043d\u0435\u043b\u044c",
        "tab_components": "\u041a\u043e\u043c\u043f\u043e\u043d\u0435\u043d\u0442\u044b",
        "tab_history": "\u0418\u0441\u0442\u043e\u0440\u0438\u044f",
        "tab_settings": "\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438",
        "tab_insights": "\u0410\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0430",
        "metric_cpu_pct": "\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 CPU %",
        "metric_cpu_temp": "\u0422\u0435\u043c\u043f. CPU",
        "metric_cpu_freq": "\u0427\u0430\u0441\u0442\u043e\u0442\u0430 CPU",
        "metric_ram_pct": "\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 RAM %",
        "metric_ram_used": "\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u043e RAM",
        "metric_disk_pct": "\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u0434\u0438\u0441\u043a\u0430 %",
        "metric_disk_r": "\u0427\u0442\u0435\u043d\u0438\u0435 \u0434\u0438\u0441\u043a\u0430",
        "metric_disk_w": "\u0417\u0430\u043f\u0438\u0441\u044c \u0434\u0438\u0441\u043a\u0430",
        "metric_net_up": "\u041e\u0442\u0434\u0430\u0447\u0430 \u0441\u0435\u0442\u044c",
        "metric_net_down": "\u041f\u0440\u0438\u0451\u043c \u0441\u0435\u0442\u044c",
        "metric_gpu_load": "\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 GPU %",
        "metric_gpu_temp": "\u0422\u0435\u043c\u043f. GPU",
        "metric_power": "\u041c\u043e\u0449\u043d\u043e\u0441\u0442\u044c (\u0412\u0442)",
        "metric_session_cost": "\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u0441\u0435\u0441\u0441\u0438\u0438",
        "power_label": "\u041c\u043e\u0449\u043d\u043e\u0441\u0442\u044c: {w:.1f} \u0412\u0442  |  \u0421\u0443\u043c\u043c. TDP: {tdp:.0f} \u0412\u0442",
        "chart_power": "\u041c\u043e\u0449\u043d\u043e\u0441\u0442\u044c (\u0412\u0442) \u043f\u043e \u0432\u0440\u0435\u043c\u0435\u043d\u0438",
        "btn_save_tdp": "\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c TDP",
        "col_name": "\u0418\u043c\u044f",
        "col_category": "\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f",
        "col_tdp": "TDP (\u0412\u0442)",
        "col_load": "\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 %",
        "col_current": "\u0422\u0435\u043a\u0443\u0449\u0430\u044f (\u0412\u0442)",
        "total_cost": "\u0418\u0442\u043e\u0433\u043e \u0441\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c: {v:.4f} {cur}",
        "total_kwh": "\u0418\u0442\u043e\u0433\u043e \u043a\u0412\u0442\u00b7\u0447: {v:.4f}",
        "col_id": "ID",
        "col_start": "\u041d\u0430\u0447\u0430\u043b\u043e",
        "col_end": "\u041a\u043e\u043d\u0435\u0446",
        "col_boot": "\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u041e\u0421",
        "col_kwh": "\u043a\u0412\u0442\u00b7\u0447",
        "col_cost": "\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c",
        "running": "\u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442",
        "yes": "\u0434\u0430",
        "no": "\u043d\u0435\u0442",
        "btn_refresh": "\u041e\u0431\u043d\u043e\u0432\u0438\u0442\u044c",
        "lbl_tariff": "\u0426\u0435\u043d\u0430 \u0437\u0430 \u043a\u0412\u0442\u00b7\u0447:",
        "lbl_currency": "\u0412\u0430\u043b\u044e\u0442\u0430:",
        "lbl_language": "\u042f\u0437\u044b\u043a:",
        "btn_save": "\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c",
        "status_running": "\u0420\u0430\u0431\u043e\u0442\u0430\u0435\u0442",
        "status_power": "\u041c\u043e\u0449\u043d\u043e\u0441\u0442\u044c: {w:.1f} \u0412\u0442 | \u0418\u0442\u043e\u0433\u043e: {c:.4f} {cur}",
        "export_csv": "\u042d\u043a\u0441\u043f\u043e\u0440\u0442 CSV",
        "recommendations": "\u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u0438",
        "threshold": "\u041f\u043e\u0440\u043e\u0433 \u043c\u043e\u0449\u043d\u043e\u0441\u0442\u0438 (\u0412\u0442):",
        "pie_title": "\u041f\u043e\u0442\u0440\u0435\u0431\u043b\u0435\u043d\u0438\u0435 \u043f\u043e \u043a\u043e\u043c\u043f\u043e\u043d\u0435\u043d\u0442\u0430\u043c",
        "monthly_forecast": "\u041f\u0440\u043e\u0433\u043d\u043e\u0437 \u0437\u0430 \u043c\u0435\u0441\u044f\u0446",
        "sessions_count": "\u0421\u0435\u0441\u0441\u0438\u0439: {n}",
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
