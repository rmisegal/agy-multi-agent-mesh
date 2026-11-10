# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""MeshContext: builds every component once from the config (shared state of the SDK mixins)."""

from __future__ import annotations

import os
from functools import cached_property
from pathlib import Path

from .client import HubClient
from .config import MeshConfig
from .constants import ENV_CONFIG_DIR
from .hub.board import TaskBoard
from .hub.gate import RateGate
from .hub.mailbox import MailboxStore
from .hub.registry import SessionRegistry
from .hub.router import HubRouter
from .hub.server import HubServer, Journal
from .instructions import InstructionWriter
from .launcher import HubLauncher
from .models import TeamSpec
from .procs import OriginGuard
from .session import SessionService
from .team import TeamLoader


class MeshContext:
    """Lazy factory. ``allow_external`` disables the in-session check for diagnostics only."""

    def __init__(self, config: MeshConfig | None = None, team_path: str | Path | None = None,
                 allow_external: bool = False, client: HubClient | None = None,
                 guard: OriginGuard | None = None) -> None:
        self.config = config or MeshConfig.load()
        self._team_path = team_path
        self.allow_external = allow_external
        if client is not None:
            self.__dict__["client"] = client
        if guard is not None:
            self.__dict__["guard"] = guard

    @cached_property
    def team(self) -> TeamSpec:
        path = self._team_path or self.config.get("team_file", "team.json")
        return TeamLoader().load(self.config.resolve(path))

    @cached_property
    def client(self) -> HubClient:
        g, rl = self.config.get, self.config.get("rate_limits.messages", {})
        client = HubClient(g("hub.host", "127.0.0.1"), int(g("hub.port", 9876)),
                           g("client.connect_timeout_s", 3.0), g("client.margin_s", 5.0),
                           rl.get("max_retries", 3), rl.get("retry_after_seconds", 2),
                           g("hub.max_message_bytes", 1_048_576))
        if g("hub.autostart", True):
            jitter = float(g("hub.autostart_jitter_s", 3.0))
            client.on_down = lambda: self.hub_launcher(client, jitter).ensure()
        return client

    def hub_launcher(self, client: HubClient, jitter_s: float = 0.0) -> HubLauncher:
        g = self.config.get
        return HubLauncher(client, self.config_dir(), float(g("hub.start_wait_s", 8.0)),
                           float(g("hub.poll_s", 0.2)), jitter_s=jitter_s)

    @cached_property
    def guard(self) -> OriginGuard:
        require = bool(self.config.get("session.require_agy_session", True))
        return OriginGuard(self.process_names, require and not self.allow_external)

    @property
    def process_names(self) -> list[str]:
        return list(self.config.get("session.process_names", ["agy.exe", "agy"]))

    @cached_property
    def session(self) -> SessionService:
        return SessionService(self.client, self.guard,
                              float(self.config.get("session.wait_timeout_s", 240)))

    @cached_property
    def writer(self) -> InstructionWriter:
        return InstructionWriter(self.config.command_prefix(),
                                 self.config.get("session.answer_file", "answer.md"))

    def config_dir(self) -> Path:
        return Path(os.environ.get(ENV_CONFIG_DIR) or self.config.root / "config")

    def build_server(self, port: int | None = None) -> HubServer:
        g = self.config.get
        mailbox = MailboxStore(int(g("queue.max_depth", 100)),
                               float(g("queue.message_ttl_s", 3600)),
                               g("queue.overflow_strategy", "reject_oldest"))
        registry = SessionRegistry(float(g("session.stale_after_s", 600)))
        journal_path = g("hub.journal", "")
        journal = Journal(self.config.resolve(journal_path) if journal_path else None)
        board_file = g("hub.board_file", "")
        board = TaskBoard(self.config.resolve(board_file) if board_file else None)
        router = HubRouter(mailbox, registry, RateGate.from_config(g("rate_limits", {})),
                           journal, board)
        return HubServer(router, g("hub.host", "127.0.0.1"),
                         int(g("hub.port", 9876) if port is None else port),
                         float(g("hub.accept_timeout_s", 1.0)),
                         int(g("hub.max_message_bytes", 1_048_576)))
