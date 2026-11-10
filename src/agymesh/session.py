# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""SessionService: the three primitives an agy session runs on itself - join, wait, reply.

``wait`` is the key idea. An interactive agy session cannot be interrupted from outside (it only
reacts to what is typed into it). So the session itself runs ONE blocking command that returns
as soon as a message arrives - the same role SendMessage's delivery plays for Claude sessions.
The failed version made the LLM poll ``inbox.ipc`` in its own loop (slow, and it forgot to).
"""

from __future__ import annotations

from pathlib import Path

from .client import HubClient
from .constants import KIND_REPLY, OP_JOIN, OP_LEAVE, OP_RECV, OP_SEND
from .models import Message, SessionInfo
from .procs import OriginGuard


class SessionService:
    """In-session commands. Every call is stamped with the agy pid by the OriginGuard."""

    def __init__(self, client: HubClient, guard: OriginGuard, wait_timeout_s: float,
                 cwd: Path | None = None) -> None:
        self.client = client
        self.guard = guard
        self.wait_timeout_s = wait_timeout_s
        self.cwd = Path(cwd) if cwd else Path.cwd()

    def _info(self, name: str, role: str = "") -> SessionInfo:
        origin = self.guard.stamp()
        return SessionInfo(name=name, role=role, agy_pid=origin["agy_pid"], cwd=str(self.cwd))

    def join(self, name: str, role: str = "") -> dict:
        return self.client.request({"op": OP_JOIN, "session": self._info(name, role).to_dict()})

    def leave(self, name: str) -> bool:
        return bool(self.client.request({"op": OP_LEAVE, "name": name}).get("left"))

    def wait(self, name: str, timeout_s: float | None = None) -> Message | None:
        timeout = self.wait_timeout_s if timeout_s is None else timeout_s
        payload = {"op": OP_RECV, "name": name, "timeout": timeout,
                   "session": self._info(name).to_dict()}
        raw = self.client.request(payload, wait_s=timeout).get("message")
        return Message.from_dict(raw) if raw else None

    def reply(self, name: str, request_id: str, text: str, to: str = "") -> Message:
        msg = Message(sender=name, to=to, content=text, kind=KIND_REPLY,
                      reply_to=request_id, origin=self.guard.stamp())
        self.client.request({"op": OP_SEND, "message": msg.to_dict()})
        return msg
