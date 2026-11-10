# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""AdminMixin: hub lifecycle, AGY.md generation and launching agy windows."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

from .constants import OP_PEERS, OP_SHUTDOWN, OP_STATS
from .launcher import TerminalLauncher
from .terminals import TerminalScanner


class AdminMixin:
    """Operations that set the mesh up; they may run from any terminal."""

    def serve_hub(self, port: int | None = None,
                  on_ready: Callable[[str, int], None] | None = None) -> int:
        """Run the hub in the foreground until Ctrl+C or ``down``. Returns the bound port."""
        server = self.build_server(port)
        bound = server.bind()
        if on_ready:
            on_ready(server.host, bound)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.stop()
        return bound

    def hub_up(self) -> bool:
        return self.hub_launcher(self.client).ensure()

    def hub_down(self) -> bool:
        if not self.client.is_up():
            return False
        self.client.request({"op": OP_SHUTDOWN})
        return True

    def status(self) -> dict:
        return self.client.request({"op": OP_STATS})

    def peers(self) -> list[dict]:
        return self.client.request({"op": OP_PEERS}).get("sessions", [])

    def write_instructions(self) -> list[Path]:
        return self.writer.write_all(self.team)

    def launch(self, names: list[str] | None = None, with_master: bool = False,
               master_only: bool = False, ping_test: bool = False) -> list[str]:
        """Open agy windows. ``ping_test``: the master runs the PING/PONG check after booting."""
        g = self.config.get
        term = TerminalLauncher(g("launch.agy_exe", "agy"), g("launch.agy_args", []),
                                g("launch.terminal", "console"))
        specs = [] if master_only else [a for a in self.team.agents
                                        if not names or a.name in names]
        opened = []
        for spec in specs:
            term.open(spec, self.writer.boot_prompt(g("launch.boot_prompt", "{name}"), spec))
            opened.append(spec.name)
        if with_master or master_only:
            master = self.team.master
            prompt = g("launch.master_boot_prompt", "{name}")
            if ping_test:
                prompt += " " + g("launch.master_ping_prompt", "").replace(
                    "{cmd}", self.config.command_prefix())
            term.open(master, self.writer.boot_prompt(prompt, master))
            opened.append(master.name)
        return opened

    def wait_for_peers(self, count: int | None = None, timeout_s: float = 300.0,
                       poll_s: float = 1.0, sleep: Callable[[float], None] = time.sleep,
                       clock: Callable[[], float] = time.monotonic) -> list[str]:
        """Block until ``count`` workers (default: the whole team) have joined; returns names."""
        want = len(self.team.agents) if count is None else count
        deadline = clock() + timeout_s
        names: list[str] = []
        while True:
            if self.client.is_up():
                names = [r["name"] for r in self.peers() if r["name"] != self.team.master.name]
            if len(names) >= want or clock() >= deadline:
                return names
            sleep(poll_s)

    def up(self, launch: bool = True, with_master: bool = False) -> dict:
        started = self.hub_up()
        files = self.write_instructions()
        opened = self.launch(with_master=with_master) if launch else []
        return {"hub_started": started, "instructions": [str(f) for f in files],
                "opened": opened}

    def terminals(self) -> list[dict]:
        sessions = self.peers() if self.client.is_up() else []
        return TerminalScanner(self.process_names).scan(sessions)
