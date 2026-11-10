# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""TerminalScanner: list the running agy processes and match them to joined mesh sessions.

The analog of ``clikit mesh terminals``: one native process snapshot, no PowerShell/WMI.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from .procs import ProcessTable


class TerminalScanner:
    def __init__(self, names: Iterable[str],
                 table_factory: Callable[[], ProcessTable] = ProcessTable) -> None:
        self.names = {n.lower() for n in names}
        self.table_factory = table_factory

    def _top_agy(self, table: ProcessTable, pid: int) -> int:
        """The outermost agy process above ``pid`` (agy may run helper agy children)."""
        top = pid
        for proc in table.ancestors(pid):
            if proc.name.lower() in self.names:
                top = proc.pid
        return top

    def scan(self, sessions: list[dict]) -> list[dict]:
        table = self.table_factory()
        joined = {self._top_agy(table, s["agy_pid"]): s for s in sessions if s.get("agy_pid")}
        rows = []
        for proc in table.by_name(self.names):
            parent = table.procs.get(proc.ppid)
            if parent and parent.name.lower() in self.names:
                continue
            session = joined.get(proc.pid)
            rows.append({
                "agy_pid": proc.pid,
                "shell": parent.name if parent else "?",
                "shell_pid": proc.ppid,
                "mesh_name": session["name"] if session else "",
                "state": session["state"] if session else "not joined",
            })
        return rows
