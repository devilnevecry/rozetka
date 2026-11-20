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