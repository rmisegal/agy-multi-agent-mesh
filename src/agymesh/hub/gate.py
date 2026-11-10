# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""RateGate: per-sender token bucket, configured from ``config/rate_limits.json``.

LLM agents that message each other can loop (A asks B, B asks A, ...). The gate caps how fast
one sender may post; the client gatekeeper backs off and retries instead of crashing.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

from ..constants import ERR_RATE_LIMITED
from ..errors import MeshError


class RateGate:
    """``requests_per_minute`` refill rate with a ``burst_size`` bucket per sender."""

    def __init__(self, requests_per_minute: float, burst_size: int, retry_after_s: float,
                 clock: Callable[[], float] = time.monotonic) -> None:
        self.rate = max(requests_per_minute, 0.001) / 60.0
        self.burst = max(burst_size, 1)
        self.retry_after_s = retry_after_s
        self.clock = clock
        self._buckets: dict[str, tuple[float, float]] = {}
        self._lock = threading.Lock()

    @classmethod
    def from_config(cls, limits: dict) -> RateGate:
        msg = (limits or {}).get("messages", {})
        return cls(msg.get("requests_per_minute", 120), msg.get("burst_size", 30),
                   msg.get("retry_after_seconds", 2))

    def check(self, sender: str) -> None:
        now = self.clock()
        with self._lock:
            tokens, last = self._buckets.get(sender, (float(self.burst), now))
            tokens = min(float(self.burst), tokens + (now - last) * self.rate)
            if tokens < 1.0:
                self._buckets[sender] = (tokens, now)
                raise MeshError(
                    f"'{sender}' is sending too fast; retry after {self.retry_after_s}s",
                    ERR_RATE_LIMITED,
                )
            self._buckets[sender] = (tokens - 1.0, now)
