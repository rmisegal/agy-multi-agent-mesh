# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""AgyMesh: the single SDK entry point. The CLI, tests and any third party call only this.

    from agymesh import AgyMesh
    mesh = AgyMesh()
    mesh.dispatch_all("Israeli winter", me="master")
"""

from __future__ import annotations

import contextlib
import json
from pathlib import Path

from .constants import KIND_PING, PING_TEXT
from .errors import MeshError
from .meshcheck import MeshChecker, MeshReport
from .models import Message
from .orchestrate import Orchestrator, Reply
from .results import ResultWriter
from .sdk_admin import AdminMixin
from .sdk_base import MeshContext
from .sdk_board import BoardMixin
from .textio import read_text_any


class AgyMesh(BoardMixin, AdminMixin, MeshContext):
    """Facade over session primitives, orchestration and administration."""

    # ---- in-session primitives (run by the agy session itself) -------------------------
    def join(self, name: str, role: str | None = None) -> dict:
        if role is None:
            role = next((a.role for a in self.team.agents if a.name == name), "")
        return self.session.join(name, role)

    def leave(self, name: str) -> bool:
        return self.session.leave(name)

    def wait(self, name: str, timeout_s: float | None = None) -> Message | None:
        return self.session.wait(name, timeout_s)

    def reply(self, name: str, request_id: str, text: str | None = None,
              file: str | Path | None = None) -> Message:
        body = read_text_any(file) if file else (text or "")
        if not body:
            raise ValueError("reply needs --text or a non-empty --file")
        return self.session.reply(name, request_id, body)

    # ---- orchestration ------------------------------------------------------------------
    def orchestrator(self, me: str | None = None) -> Orchestrator:
        g = self.config.get
        return Orchestrator(self.client, self.guard, me or self.team.master.name,
                            float(g("orchestrator.reply_timeout_s", 600)),
                            float(g("orchestrator.ping_timeout_s", 120)))

    def send(self, to: str, text: str, me: str | None = None,
             timeout_s: float | None = None) -> Reply:
        return self.orchestrator(me).send(to, text, timeout_s=timeout_s)

    def dispatch(self, tasks: dict[str, str], me: str | None = None,
                 timeout_s: float | None = None) -> dict[str, Reply]:
        return self.orchestrator(me).fan_out(tasks, timeout_s=timeout_s)

    def dispatch_all(self, topic: str, me: str | None = None,
                     timeout_s: float | None = None) -> dict[str, Reply]:
        tasks = {a.name: a.task_for(topic) for a in self.team.agents}
        return self.dispatch(tasks, me, timeout_s)

    def ping_targets(self, me: str, exclude: list[str] | None = None) -> list[str]:
        skip = {me, self.team.master.name, *(exclude or [])}
        return [row["name"] for row in self.peers() if row["name"] not in skip]

    def ping_all(self, me: str | None = None,
                 exclude: list[str] | None = None) -> dict[str, Reply]:
        orch = self.orchestrator(me)
        return orch.ping_all(self.ping_targets(orch.me, exclude))

    def relay_pings(self, me: str, reply_to: str,
                    exclude: list[str] | None = None) -> dict[str, str]:
        """Mesh-check leg run by a worker: post PINGs, reply with their ids, do NOT wait."""
        orch = self.orchestrator(me)
        origin = self.guard.stamp()
        sent: dict[str, str] = {}
        for peer in self.ping_targets(orch.me, exclude):
            with contextlib.suppress(MeshError):
                sent[peer] = orch.post(peer, PING_TEXT, KIND_PING, origin).id
        self.session.reply(orch.me, reply_to, json.dumps({"sent": sent}))
        return sent

    def save_result(self, title: str, results: dict[str, Reply]) -> Path:
        g = self.config.get
        writer = ResultWriter(self.config.resolve(g("orchestrator.results_dir", ".mesh/results")),
                              bool(g("orchestrator.open_result", True)))
        return writer.save(title, results)

    def mesh_check(self, me: str | None = None) -> MeshReport:
        orch = self.orchestrator(me)
        return MeshChecker(orch).run(self.ping_targets(orch.me))
