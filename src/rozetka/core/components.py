"""PC component model and TDP-based power estimation."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class ComponentCategory(str, Enum):
    CPU = "cpu"
    GPU = "gpu"
    RAM = "ram"
    DISK = "disk"
    MOTHERBOARD = "motherboard"
    PSU = "psu"
    COOLING = "cooling"
    OTHER = "other"


@dataclass
class Component:
    name: str
    category: ComponentCategory
    tdp_watts: float = 0.0
    idle_watts: float = 0.0
    load: float = 0.0  # 0..1
    current_watts: float = 0.0

    def estimate_watts(self) -> float:
        base = self.idle_watts if self.idle_watts > 0 else self.tdp_watts * 0.15
        return base + (self.tdp_watts - base) * max(0.0, min(1.0, self.load))

    def update_load(self, load: float) -> None:
        self.load = max(0.0, min(1.0, load))
        self.current_watts = self.estimate_watts()


@dataclass
class ComponentRegistry:
    components: List[Component] = field(default_factory=list)

    def add(self, c: Component) -> None:
        self.components.append(c)

    def by_category(self, cat: ComponentCategory) -> List[Component]:
        return [c for c in self.components if c.category == cat]

    def total_watts(self) -> float:
        return sum(c.current_watts for c in self.components)

    def total_tdp(self) -> float:
        return sum(c.tdp_watts for c in self.components)

    def as_dict(self) -> Dict[str, float]:
        return {c.name: c.current_watts for c in self.components}

import psutil


def build_default_registry() -> "ComponentRegistry":
    reg = ComponentRegistry()
    # CPU
    try:
        cpu_name = psutil.cpu_freq().max and "CPU" or "CPU"
    except Exception:
        cpu_name = "CPU"
    cpu_tdp = 65.0
    # heuristic by core count
    cores = psutil.cpu_count(logical=False) or 4
    if cores >= 16:
        cpu_tdp = 125.0
    elif cores >= 8:
        cpu_tdp = 95.0
    reg.add(Component(name=f"CPU ({cores} cores)", category=ComponentCategory.CPU, tdp_watts=cpu_tdp, idle_watts=cpu_tdp * 0.1))
    # RAM
    total_gb = psutil.virtual_memory().total / 1e9
    ram_tdp = max(3.0, total_gb * 0.3)
    reg.add(Component(name=f"RAM ({total_gb:.0f} GB)", category=ComponentCategory.RAM, tdp_watts=ram_tdp, idle_watts=ram_tdp * 0.3))
    # Disks
    seen = set()
    for part in psutil.disk_partitions():
        if part.device in seen:
            continue
        seen.add(part.device)
        reg.add(Component(name=f"Disk {part.device}", category=ComponentCategory.DISK, tdp_watts=5.0, idle_watts=0.5))
    if not seen:
        reg.add(Component(name="Disk", category=ComponentCategory.DISK, tdp_watts=5.0, idle_watts=0.5))
    # GPU via NVML if available
    try:
        import pynvml
        pynvml.nvmlInit()
        h = pynvml.nvmlDeviceGetHandleByIndex(0)
        name = pynvml.nvmlDeviceGetName(h)
        if isinstance(name, bytes):
            name = name.decode()
        reg.add(Component(name=f"GPU ({name})", category=ComponentCategory.GPU, tdp_watts=150.0, idle_watts=15.0))
    except Exception:
        reg.add(Component(name="GPU (unknown)", category=ComponentCategory.GPU, tdp_watts=100.0, idle_watts=10.0))
    reg.add(Component(name="Motherboard", category=ComponentCategory.MOTHERBOARD, tdp_watts=30.0, idle_watts=15.0))
    reg.add(Component(name="Cooling", category=ComponentCategory.COOLING, tdp_watts=15.0, idle_watts=5.0))
    return reg
