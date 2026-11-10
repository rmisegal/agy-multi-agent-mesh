# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""Orchestrator: send one message, or fan out many in parallel and gather the replies.

``dispatch`` posts every sub-task first and only then waits, so the agents work in parallel and
the whole round costs the master ONE shell command (the failed master spent 20 minutes issuing
one command per agent and polling files between LLM turns).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from .client import HubClient
from .constants import KIND_PING, KIND_TASK, OP_AWAIT, OP_SEND, PING_TEXT
from .errors import MeshError
from .models import Message
from .procs import OriginGuard


@dataclass
class Reply:
    """Outcome of one request: the reply message, or why there is none."""

    peer: str
    message: Message | None = None
    error: str = ""
    request: Message | None = None

    @property
    def ok(self) -> bool:
        return self.message is not None

    @property
    def text(self) -> str:
        return self.message.content if self.message else ""

    @property
    def elapsed_s(self) -> float | None:
        if self.message and self.request:
            return round(self.message.created - self.request.created, 2)
        return None

    @property
    def answered_by(self) -> str:
        if not self.message:
            return ""
        pid = self.message.origin.get("agy_pid")
        return f"agy pid {pid}" if pid else "external terminal (not an agy session!)"


class Orchestrator:
    """Sender side of the mesh, used by the master and by workers running ``ping-all``."""

    def __init__(self, client: HubClient, guard: OriginGuard, me: str,
                 reply_timeout_s: float, ping_timeout_s: float,
                 clock: Callable[[], float] = time.monotonic) -> None:
        self.client, self.guard, self.me = client, guard, me
        self.reply_timeout_s, self.ping_timeout_s = reply_timeout_s, ping_timeout_s
        self.clock = clock

    def post(self, to: str, text: str, kind: str = KIND_TASK,
             origin: dict | None = None) -> Message:
        msg = Message(sender=self.me, to=to, content=text, kind=kind,
                      origin=origin if origin is not None else self.guard.stamp())
        self.client.request({"op": OP_SEND, "message": msg.to_dict()})
        return msg

    def await_ids(self, ids: dict, timeout_s: float) -> dict:
        """Wait for the replies to any request ids (``key -> id``) under one shared deadline.

        Any session may collect a reply by id - that is what lets mesh-check run in parallel.
        """
        deadline = self.clock() + timeout_s
        out: dict = {}
        for key, request_id in ids.items():
            left = max(0.0, deadline - self.clock())
            raw = self.client.request({"op": OP_AWAIT, "id": request_id, "timeout": left},
                                      wait_s=left).get("message")
            out[key] = Message.from_dict(raw) if raw else None
        return out

    def collect(self, sent: dict[str, Message], timeout_s: float) -> dict[str, Reply]:
        got = self.await_ids({peer: req.id for peer, req in sent.items()}, timeout_s)
        err = f"no reply within {timeout_s:.0f}s (busy, stuck, or not waiting)"
        return {peer: Reply(peer, got[peer], "" if got[peer] else err, req)
                for peer, req in sent.items()}

    def fan_out(self, tasks: dict[str, str], kind: str = KIND_TASK,
                timeout_s: float | None = None) -> dict[str, Reply]:
        origin = self.guard.stamp()  # once, and fatal: a plain terminal must not send at all
        sent: dict[str, Message] = {}
        failed: dict[str, Reply] = {}
        for peer, text in tasks.items():
            try:
                sent[peer] = self.post(peer, text, kind, origin)
            except (MeshError, OSError) as exc:
                failed[peer] = Reply(peer, error=str(exc))
        got = self.collect(sent, self.reply_timeout_s if timeout_s is None else timeout_s)
        return {peer: failed.get(peer) or got[peer] for peer in tasks}

    def send(self, to: str, text: str, kind: str = KIND_TASK,
             timeout_s: float | None = None) -> Reply:
        return self.fan_out({to: text}, kind, timeout_s)[to]

    def ping_all(self, peers: list[str]) -> dict[str, Reply]:
        return self.fan_out(dict.fromkeys(peers, PING_TEXT), KIND_PING, self.ping_timeout_s)
