# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""ProcessTable + OriginGuard: prove that a mesh command runs INSIDE an agy session.

When an agy session runs a shell command, the process tree is ``agy -> shell -> uv -> python``.
Walking up from our own pid until we meet an agy process proves the message was sent by the
session itself, not typed in an external terminal. The pid is stamped on every message.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from .errors import NotInSessionError
from .procs_native import snapshot as native_snapshot

MAX_DEPTH = 32


@dataclass(frozen=True)
class Proc:
    pid: int
    ppid: int
    name: str


class ProcessTable:
    """Snapshot of the process list with ancestor walks (cycle-safe: pids can be reused)."""

    def __init__(self, snapshot: Callable[[], dict[int, tuple[int, str]]] | None = None) -> None:
        raw = (snapshot or native_snapshot)()
        self.procs = {pid: Proc(pid, ppid, name) for pid, (ppid, name) in raw.items()}

    def ancestors(self, pid: int) -> list[Proc]:
        chain, seen = [], set()
        current = self.procs.get(pid)
        while current and current.pid not in seen and len(chain) < MAX_DEPTH:
            seen.add(current.pid)
            chain.append(current)
            current = self.procs.get(current.ppid)
        return chain

    def find_ancestor(self, pid: int, names: Iterable[str]) -> Proc | None:
        wanted = {n.lower() for n in names}
        for proc in self.ancestors(pid)[1:]:
            if proc.name.lower() in wanted:
                return proc
        return None

    def by_name(self, names: Iterable[str]) -> list[Proc]:
        wanted = {n.lower() for n in names}
        return sorted((p for p in self.procs.values() if p.name.lower() in wanted),
                      key=lambda p: p.pid)


class OriginGuard:
    """Stamps messages with the sending agy pid; refuses plain terminals when required."""

    def __init__(self, names: Iterable[str], require: bool,
                 table_factory: Callable[[], ProcessTable] = ProcessTable,
                 pid: int | None = None) -> None:
        self.names = list(names)
        self.require = require
        self.table_factory = table_factory
        self.pid = pid if pid is not None else os.getpid()

    def stamp(self) -> dict:
        agy = self.table_factory().find_ancestor(self.pid, self.names)
        if agy is None and self.require:
            raise NotInSessionError(
                "This mesh command must be run BY an agy session (its shell tool), not typed "
                "in a plain terminal. Ask the agy session to run it, or add --allow-external "
                "for a one-off diagnostic."
            )
        return {"agy_pid": agy.pid if agy else None, "external": agy is None}
