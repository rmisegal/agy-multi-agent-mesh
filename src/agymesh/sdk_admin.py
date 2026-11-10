# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""AdminMixin: hub lifecycle, AGY.md generation and launching agy windows."""

from __future__ import annotations

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

    def launch(self, names: list[str] | None = None, with_master: bool = False) -> list[str]:
        g = self.config.get
        term = TerminalLauncher(g("launch.agy_exe", "agy"), g("launch.agy_args", []),
                                g("launch.terminal", "console"))
        specs = [a for a in self.team.agents if not names or a.name in names]
        opened = []
        for spec in specs:
            term.open(spec, self.writer.boot_prompt(g("launch.boot_prompt", "{name}"), spec))
            opened.append(spec.name)
        if with_master:
            master = self.team.master
            term.open(master, self.writer.boot_prompt(g("launch.master_boot_prompt", "{name}"),
                                                      master))
            opened.append(master.name)
        return opened

    def up(self, launch: bool = True, with_master: bool = False) -> dict:
        started = self.hub_up()
        files = self.write_instructions()
        opened = self.launch(with_master=with_master) if launch else []
        return {"hub_started": started, "instructions": [str(f) for f in files],
                "opened": opened}

    def terminals(self) -> list[dict]:
        sessions = self.peers() if self.client.is_up() else []
        return TerminalScanner(self.process_names).scan(sessions)
