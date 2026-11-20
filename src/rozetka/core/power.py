"""Power and cost calculation helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .components import Component, ComponentRegistry
from .monitor import SystemSnapshot


@dataclass
class Tariff:
    price_per_kwh: float = 5.0  # currency per kWh
    currency: str = "RUB"


def update_registry_from_snapshot(reg: ComponentRegistry, snap: SystemSnapshot) -> None:
    """Map a system snapshot onto component loads (best-effort)."""
    cpu_load = snap.cpu.percent / 100.0
    for c in reg.by_category(__import__("rozetka.core.components", fromlist=["ComponentCategory"]).ComponentCategory.CPU):
        c.update_load(cpu_load)
    mem_load = snap.memory.percent / 100.0
    for c in reg.by_category(__import__("rozetka.core.components", fromlist=["ComponentCategory"]).ComponentCategory.RAM):
        c.update_load(mem_load)
    disk_load = min(1.0, (snap.disk.read_bytes_s + snap.disk.write_bytes_s) / (100 * 1024 * 1024))
    for c in reg.by_category(__import__("rozetka.core.components", fromlist=["ComponentCategory"]).ComponentCategory.DISK):
        c.update_load(disk_load)
    # GPU
    if snap.gpus:
        gpu_load = snap.gpus[0].load
        gpu_power = snap.gpus[0].power_w
        for c in reg.by_category(__import__("rozetka.core.components", fromlist=["ComponentCategory"]).ComponentCategory.GPU):
            c.update_load(gpu_load)
            if gpu_power is not None:
                c.current_watts = gpu_power
    # Motherboard / cooling baseline
    for c in reg.by_category(__import__("rozetka.core.components", fromlist=["ComponentCategory"]).ComponentCategory.MOTHERBOARD):
        c.update_load(0.5)
    for c in reg.by_category(__import__("rozetka.core.components", fromlist=["ComponentCategory"]).ComponentCategory.COOLING):
        c.update_load(max(cpu_load, 0.3))


def total_power_watts(reg: ComponentRegistry) -> float:
    return reg.total_watts()


def kwh_from_watts(watts: float, seconds: float) -> float:
    return watts * seconds / 3_600_000.0


def cost_for_energy(kwh: float, tariff: Tariff) -> float:
    return kwh * tariff.price_per_kwh


def session_cost(reg_samples: list, tariff: Tariff) -> float:
    """Integrate power samples (list of (watts, seconds)) into cost."""
    total_kwh = 0.0
    for watts, seconds in reg_samples:
        total_kwh += kwh_from_watts(watts, seconds)
    return cost_for_energy(total_kwh, tariff)