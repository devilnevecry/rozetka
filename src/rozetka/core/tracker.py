"""Session and boot tracking with energy/cost accounting."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PowerSample:
    timestamp: float
    watts: float


@dataclass
class Session:
    id: Optional[int] = None
    start_ts: float = field(default_factory=time.time)
    end_ts: Optional[float] = None
    is_boot: bool = False
    samples: List[PowerSample] = field(default_factory=list)

    def add_sample(self, watts: float) -> None:
        self.samples.append(PowerSample(timestamp=time.time(), watts=watts))

    def duration_seconds(self) -> float:
        end = self.end_ts if self.end_ts else time.time()
        return max(0.0, end - self.start_ts)

    def total_kwh(self) -> float:
        if len(self.samples) < 2:
            if self.samples:
                return self.samples[0].watts * self.duration_seconds() / 3_600_000.0
            return 0.0
        total = 0.0
        for i in range(1, len(self.samples)):
            dt = self.samples[i].timestamp - self.samples[i - 1].timestamp
            if dt <= 0:
                continue
            avg_w = (self.samples[i].watts + self.samples[i - 1].watts) / 2.0
            total += avg_w * dt / 3_600_000.0
        # tail
        last = self.samples[-1]
        now = self.end_ts if self.end_ts else time.time()
        dt = now - last.timestamp
        if dt > 0:
            total += last.watts * dt / 3_600_000.0
        return total

    def close(self) -> None:
        self.end_ts = time.time()


class SessionTracker:
    def __init__(self) -> None:
        self.current: Optional[Session] = None
        self.history: List[Session] = []

    def start_session(self, is_boot: bool = False) -> Session:
        if self.current is not None:
            self.current.close()
            self.history.append(self.current)
        self.current = Session(is_boot=is_boot)
        return self.current

    def record(self, watts: float) -> None:
        if self.current is None:
            self.start_session(is_boot=False)
        assert self.current is not None
        self.current.add_sample(watts)

    def end_session(self) -> Optional[Session]:
        if self.current is None:
            return None
        self.current.close()
        finished = self.current
        self.history.append(finished)
        self.current = None
        return finished

    def all_sessions(self) -> List[Session]:
        out = list(self.history)
        if self.current is not None:
            out.append(self.current)
        return out