"""System resource monitoring using psutil (+ optional GPU backends)."""
from __future__ import annotations

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

import psutil

try:
    import pynvml  # type: ignore

    _NVML = True
except Exception:  # pragma: no cover - optional
    pynvml = None
    _NVML = False


@dataclass
class CpuMetrics:
    percent: float = 0.0
    per_core: List[float] = field(default_factory=list)
    freq_mhz: float = 0.0
    temp_c: Optional[float] = None


@dataclass
class MemoryMetrics:
    total_gb: float = 0.0
    used_gb: float = 0.0
    percent: float = 0.0


@dataclass
class DiskMetrics:
    read_bytes_s: float = 0.0
    write_bytes_s: float = 0.0
    percent: float = 0.0


@dataclass
class NetMetrics:
    sent_bytes_s: float = 0.0
    recv_bytes_s: float = 0.0


@dataclass
class GpuMetrics:
    name: str = ""
    load: float = 0.0
    memory_used_mb: float = 0.0
    memory_total_mb: float = 0.0
    temp_c: Optional[float] = None
    power_w: Optional[float] = None


@dataclass
class SystemSnapshot:
    timestamp: float = 0.0
    cpu: CpuMetrics = field(default_factory=CpuMetrics)
    memory: MemoryMetrics = field(default_factory=MemoryMetrics)
    disk: DiskMetrics = field(default_factory=DiskMetrics)
    net: NetMetrics = field(default_factory=NetMetrics)
    gpus: List[GpuMetrics] = field(default_factory=list)
    uptime_seconds: float = 0.0


class SystemMonitor:
    """Collects snapshots in a background thread at a fixed interval."""

    def __init__(self, interval: float = 1.0) -> None:
        self.interval = interval
        self._callbacks: List[Callable[[SystemSnapshot], None]] = []
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._last_disk = psutil.disk_io_counters()
        self._last_net = psutil.net_io_counters()
        self._last_time = time.time()
        self._nvml_handle = None
        if _NVML:
            try:
                pynvml.nvmlInit()
                self._nvml_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            except Exception:
                self._nvml_handle = None

    def subscribe(self, cb: Callable[[SystemSnapshot], None]) -> None:
        self._callbacks.append(cb)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def _loop(self) -> None:
        while not self._stop.is_set():
            snap = self.collect()
            for cb in self._callbacks:
                try:
                    cb(snap)
                except Exception:
                    pass
            self._stop.wait(self.interval)

    def collect(self) -> SystemSnapshot:
        now = time.time()
        snap = SystemSnapshot(timestamp=now)
        # CPU
        cpu_percent = psutil.cpu_percent(interval=None)
        snap.cpu.percent = cpu_percent
        snap.cpu.per_core = psutil.cpu_percent(interval=None, percpu=True) or []
        freq = psutil.cpu_freq()
        snap.cpu.freq_mhz = freq.current if freq else 0.0
        # temps
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name in ("coretemp", "cpu_thermal", "k10temp"):
                    if name in temps and temps[name]:
                        snap.cpu.temp_c = temps[name][0].current
                        break
                if snap.cpu.temp_c is None:
                    first = next(iter(temps.values()))
                    if first:
                        snap.cpu.temp_c = first[0].current
        except Exception:
            snap.cpu.temp_c = None
        # Memory
        vm = psutil.virtual_memory()
        snap.memory.total_gb = vm.total / 1e9
        snap.memory.used_gb = vm.used / 1e9
        snap.memory.percent = vm.percent
        # Disk
        dio = psutil.disk_io_counters()
        dt = now - self._last_time if now > self._last_time else 1.0
        if dio and self._last_disk:
            snap.disk.read_bytes_s = max(0.0, (dio.read_bytes - self._last_disk.read_bytes) / dt)
            snap.disk.write_bytes_s = max(0.0, (dio.write_bytes - self._last_disk.write_bytes) / dt)
        du = psutil.disk_usage("/")
        snap.disk.percent = du.percent
        # Net
        nio = psutil.net_io_counters()
        if nio and self._last_net:
            snap.net.sent_bytes_s = max(0.0, (nio.bytes_sent - self._last_net.bytes_sent) / dt)
            snap.net.recv_bytes_s = max(0.0, (nio.bytes_recv - self._last_net.bytes_recv) / dt)
        self._last_disk = dio
        self._last_net = nio
        self._last_time = now
        # Uptime
        snap.uptime_seconds = time.time() - psutil.boot_time()
        # GPU
        snap.gpus = self._collect_gpu()
        return snap

    def _collect_gpu(self) -> List[GpuMetrics]:
        gpus: List[GpuMetrics] = []
        if self._nvml_handle is not None:
            try:
                name = pynvml.nvmlDeviceGetName(self._nvml_handle)
                if isinstance(name, bytes):
                    name = name.decode()
                util = pynvml.nvmlDeviceGetUtilizationRates(self._nvml_handle)
                mem = pynvml.nvmlDeviceGetMemoryInfo(self._nvml_handle)
                try:
                    temp = pynvml.nvmlDeviceGetTemperature(self._nvml_handle, pynvml.NVML_TEMPERATURE_GPU)
                except Exception:
                    temp = None
                try:
                    power = pynvml.nvmlDeviceGetPowerUsage(self._nvml_handle) / 1000.0
                except Exception:
                    power = None
                gpus.append(GpuMetrics(
                    name=name,
                    load=util.gpu / 100.0,
                    memory_used_mb=mem.used / 1e6,
                    memory_total_mb=mem.total / 1e6,
                    temp_c=temp,
                    power_w=power,
                ))
            except Exception:
                pass
        return gpus