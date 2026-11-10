# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""SessionRegistry: who joined the mesh, from which agy pid, and whether it is listening now.

This is the ``ListAgents`` analog. Unlike the failed version (which only knew a hard-coded list
art/poem/joke), membership comes from sessions that really ran ``join``.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

from ..constants import STATE_STALE
from ..models import SessionInfo


class SessionRegistry:
    """Thread-safe name -> SessionInfo map; a session unseen for ``stale_after_s`` is stale."""

    def __init__(self, stale_after_s: float, clock: Callable[[], float] = time.time) -> None:
        self.stale_after_s = stale_after_s
        self.clock = clock
        self._sessions: dict[str, SessionInfo] = {}
        self._lock = threading.Lock()

    def join(self, info: SessionInfo) -> SessionInfo:
        now = self.clock()
        info.joined = info.last_seen = now
        with self._lock:
            self._sessions[info.name] = info
        return info

    def leave(self, name: str) -> bool:
        with self._lock:
            return self._sessions.pop(name, None) is not None

    def known(self, name: str) -> bool:
        with self._lock:
            return name in self._sessions

    def touch(self, name: str, state: str) -> None:
        with self._lock:
            info = self._sessions.get(name)
            if info:
                info.state = state
                info.last_seen = self.clock()

    def names(self) -> list[str]:
        with self._lock:
            return sorted(self._sessions)

    def rows(self) -> list[dict]:
        now = self.clock()
        with self._lock:
            rows = []
            for info in sorted(self._sessions.values(), key=lambda s: s.name):
                row = info.to_dict()
                if now - info.last_seen > self.stale_after_s:
                    row["state"] = STATE_STALE
                row["idle_s"] = round(now - info.last_seen, 1)
                rows.append(row)
            return rows
