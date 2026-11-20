from rozetka.core.components import Component, ComponentCategory, ComponentRegistry
from rozetka.core.power import Tariff, cost_for_energy, kwh_from_watts, total_power_watts, update_registry_from_snapshot
from rozetka.core.monitor import SystemSnapshot, CpuMetrics, MemoryMetrics


def test_kwh_from_watts():
    assert abs(kwh_from_watts(1000.0, 3600.0) - 1.0) < 1e-9


def test_cost_for_energy():
    t = Tariff(price_per_kwh=5.0)
    assert cost_for_energy(2.0, t) == 10.0


def test_total_power_watts():
    reg = ComponentRegistry()
    reg.add(Component(name="CPU", category=ComponentCategory.CPU, tdp_watts=100.0, idle_watts=10.0, load=1.0, current_watts=100.0))
    assert total_power_watts(reg) == 100.0


def test_update_registry_from_snapshot():
    reg = ComponentRegistry()
    reg.add(Component(name="CPU", category=ComponentCategory.CPU, tdp_watts=100.0, idle_watts=10.0))
    snap = SystemSnapshot(cpu=CpuMetrics(percent=50.0), memory=MemoryMetrics(percent=40.0))
    update_registry_from_snapshot(reg, snap)
    cpu = reg.by_category(ComponentCategory.CPU)[0]
    assert abs(cpu.load - 0.5) < 1e-9
    assert cpu.current_watts > 10.0