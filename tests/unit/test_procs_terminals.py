# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""ProcessTable, OriginGuard and TerminalScanner on a fake process tree."""

from __future__ import annotations

import os

import pytest

from agymesh.errors import NotInSessionError
from agymesh.procs import OriginGuard, ProcessTable
from agymesh.procs_native import snapshot
from agymesh.terminals import TerminalScanner

# explorer(1) -> pwsh(10) -> agy(20) -> agy helper(21) -> pwsh(30) -> uv(40) -> python(50)
TREE = {1: (0, "explorer.exe"), 10: (1, "pwsh.exe"), 20: (10, "agy.exe"), 21: (20, "agy.exe"),
        30: (21, "pwsh.exe"), 40: (30, "uv.exe"), 50: (40, "python.exe"),
        60: (1, "pwsh.exe"), 70: (60, "python.exe"), 80: (80, "loop.exe")}
NAMES = ["agy.exe", "agy"]


def table() -> ProcessTable:
    return ProcessTable(lambda: TREE)


class TestProcessTable:
    def test_ancestor_walk_and_find(self):
        assert [p.pid for p in table().ancestors(50)] == [50, 40, 30, 21, 20, 10, 1]
        assert table().find_ancestor(50, NAMES).pid == 21
        assert table().find_ancestor(70, NAMES) is None

    def test_cycles_terminate(self):
        assert [p.pid for p in table().ancestors(80)] == [80]

    def test_by_name(self):
        assert [p.pid for p in table().by_name(["AGY.EXE"])] == [20, 21]

    def test_native_snapshot_contains_this_process(self):
        assert os.getpid() in snapshot()


class TestOriginGuard:
    def test_stamp_inside_session(self):
        assert OriginGuard(NAMES, True, table, pid=50).stamp() == {"agy_pid": 21,
                                                                    "external": False}

    def test_plain_terminal_refused_or_marked(self):
        with pytest.raises(NotInSessionError, match="agy session"):
            OriginGuard(NAMES, True, table, pid=70).stamp()
        assert OriginGuard(NAMES, False, table, pid=70).stamp() == {"agy_pid": None,
                                                                     "external": True}


class TestTerminalScanner:
    def test_top_level_agy_matched_to_session(self):
        rows = TerminalScanner(NAMES, table).scan(
            [{"name": "poem", "agy_pid": 21, "state": "listening"}, {"name": "x"}])
        assert rows == [{"agy_pid": 20, "shell": "pwsh.exe", "shell_pid": 10,
                         "mesh_name": "poem", "state": "listening"}]

    def test_unjoined_agy(self):
        rows = TerminalScanner(NAMES, table).scan([])
        assert rows[0]["state"] == "not joined" and rows[0]["mesh_name"] == ""
