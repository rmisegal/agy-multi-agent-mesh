# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""HubLauncher, TerminalLauncher (spawn mocked) and the AGY.md InstructionWriter."""

from __future__ import annotations

import subprocess
import sys

import pytest

from agymesh.errors import HubUnavailableError, MeshError
from agymesh.instructions import InstructionWriter
from agymesh.launcher import BREAKAWAY, HubLauncher, TerminalLauncher
from agymesh.models import AgentSpec
from agymesh.team import TeamLoader
from agymesh.textio import fill, read_text_any
from tests.conftest import team_copy


class FakeClient:
    def __init__(self, ups):
        self.ups = list(ups)

    def is_up(self):
        return self.ups.pop(0) if self.ups else False


class Spawn:
    def __init__(self, fail_first=False):
        self.calls, self.fail_first = [], fail_first

    def __call__(self, argv, **kw):
        self.calls.append((argv, kw))
        if self.fail_first and len(self.calls) == 1:
            raise OSError("breakaway not allowed")


class TestHubLauncher:
    def make(self, ups, spawn, tmp_path, wait=1.0):
        ticks = iter(range(100))
        return HubLauncher(FakeClient(ups), tmp_path, wait, 0.1, spawn,
                           sleep=lambda s: None, clock=lambda: next(ticks) * 0.1)

    def test_reuses_running_hub(self, tmp_path):
        spawn = Spawn()
        assert self.make([True], spawn, tmp_path).ensure() is False and not spawn.calls

    def test_starts_hub_retrying_without_breakaway(self, tmp_path):
        spawn = Spawn(fail_first=True)
        assert self.make([False, False, True], spawn, tmp_path).ensure() is True
        assert spawn.calls[0][0][-2:] == ["agymesh", "hub"] and len(spawn.calls) == 2
        assert spawn.calls[1][1]["env"]["AGYMESH_CONFIG_DIR"] == str(tmp_path)

    def test_random_delay_then_recheck_skips_spawn_when_another_agent_won(self, tmp_path):
        spawn, naps = Spawn(), []
        launcher = HubLauncher(FakeClient([False, True]), tmp_path, spawn=spawn,
                               sleep=naps.append, jitter_s=3.0, rand=lambda a, b: b / 2)
        assert launcher.ensure() is False
        assert naps == [1.5] and spawn.calls == []

    def test_gives_up_with_a_reason(self, tmp_path):
        with pytest.raises(HubUnavailableError, match="did not start"):
            self.make([False], Spawn(), tmp_path, wait=0.3).ensure()


class TestTerminalLauncher:
    def test_console_window_runs_agy_interactive_with_boot_prompt(self, tmp_path):
        spawn = Spawn()
        spec = AgentSpec("poem", tmp_path / "poem")
        argv = TerminalLauncher("agy", ["--x"], "console", spawn, which=lambda n: n).open(
            spec, "boot; now")
        assert argv == ["agy", "--x", "-i", "boot; now"] and spec.folder.is_dir()
        assert spawn.calls[0][1]["cwd"] == str(spec.folder)

    def test_windows_terminal_tab_escapes_semicolons(self, tmp_path):
        spawn = Spawn()
        TerminalLauncher("agy", [], "wt", spawn, which=lambda n: n).open(
            AgentSpec("art", tmp_path / "art"), "a; b")
        assert spawn.calls[0][0][:4] == ["wt", "-w", "0", "nt"]
        assert spawn.calls[0][0][-1] == "a, b"

    @pytest.mark.skipif(sys.platform != "win32", reason="job objects are Windows-only")
    def test_windows_break_away_from_the_callers_job(self, tmp_path):
        # Run BY an agy session, the windows must outlive the tool call's job object.
        spawn = Spawn()
        TerminalLauncher("agy", [], "console", spawn, which=lambda n: n).open(
            AgentSpec("joke", tmp_path / "joke"), "b")
        flags = spawn.calls[0][1]["creationflags"]
        assert flags & BREAKAWAY and flags & subprocess.CREATE_NEW_CONSOLE
        spawn = Spawn()
        TerminalLauncher("agy", [], "wt", spawn, which=lambda n: n).open(
            AgentSpec("art", tmp_path / "art"), "b")
        assert spawn.calls[0][1]["creationflags"] & BREAKAWAY

    @pytest.mark.skipif(sys.platform != "win32", reason="job objects are Windows-only")
    def test_windows_retry_without_breakaway_when_the_job_forbids_it(self, tmp_path):
        spawn = Spawn(fail_first=True)
        TerminalLauncher("agy", [], "console", spawn, which=lambda n: n).open(
            AgentSpec("poem", tmp_path / "poem"), "b")
        assert len(spawn.calls) == 2
        assert spawn.calls[1][1]["creationflags"] == subprocess.CREATE_NEW_CONSOLE
        assert spawn.calls[1][1]["cwd"] == str(tmp_path / "poem")

    def test_missing_agy_is_explained(self, tmp_path):
        with pytest.raises(MeshError, match="not found on PATH"):
            TerminalLauncher("agy", [], which=lambda n: None).open(AgentSpec("a", tmp_path), "b")


class TestInstructionWriter:
    def test_writes_master_and_worker_files_with_commands(self, tmp_path):
        team = TeamLoader().load(team_copy(tmp_path))
        paths = InstructionWriter("AGYCMD", "answer.md").write_all(team)
        assert [p.parent.name for p in paths] == ["master", "art", "poem", "joke"]
        worker = paths[2].read_text(encoding="utf-8")
        assert "AGYCMD wait --name poem" in worker and "{{" not in worker
        assert "4 rhyming lines in Hebrew" in worker
        master = paths[0].read_text(encoding="utf-8")
        assert "`joke` - Humorist" in master and "dispatch-all --name master" in master

    def test_boot_prompt(self):
        assert InstructionWriter.boot_prompt("agent '{name}'", AgentSpec("x", None)) == "agent 'x'"


def test_textio_reads_any_encoding_and_fills(tmp_path):
    f = tmp_path / "a.md"
    f.write_bytes("שלום\n".encode("utf-16"))
    assert read_text_any(f) == "שלום"
    f.write_bytes("﻿hello ".encode())
    assert read_text_any(f) == "hello"
    assert fill("{{a}}-{{b}}", a="1") == "1-{{b}}"
