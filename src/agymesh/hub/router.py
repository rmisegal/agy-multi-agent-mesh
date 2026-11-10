# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""HubRouter: pure request -> response logic of the hub (no sockets, fully unit-testable).

Fixes of the failed hub, in order: an unknown target is an explicit error (it used to be dropped
silently, leaving the sender waiting forever); replies are matched by request id (a stale
``response.ipc`` used to be taken as the new answer); every message is journaled.
"""

from __future__ import annotations

import threading
from collections.abc import Callable

from .. import constants as c
from ..errors import MeshError
from ..models import Message, SessionInfo
from ..version import __version__
from .board import TaskBoard
from .gate import RateGate
from .mailbox import MailboxStore
from .registry import SessionRegistry
from .router_board import BoardOpsMixin


class HubRouter(BoardOpsMixin):
    """Dispatches one request dict to its handler and always answers with ``{"ok": ...}``."""

    def __init__(self, mailbox: MailboxStore, registry: SessionRegistry, gate: RateGate,
                 journal: Callable[[str, dict], None] | None = None,
                 board: TaskBoard | None = None) -> None:
        self.mailbox = mailbox
        self.registry = registry
        self.gate = gate
        self.board = board or TaskBoard()
        self.journal = journal or (lambda event, data: None)
        self.stop_event = threading.Event()
        self._ops = {
            c.OP_HELLO: self._hello, c.OP_JOIN: self._join, c.OP_LEAVE: self._leave,
            c.OP_SEND: self._send, c.OP_RECV: self._recv, c.OP_AWAIT: self._await,
            c.OP_PEERS: self._peers, c.OP_STATS: self._stats, c.OP_SHUTDOWN: self._shutdown,
            **self.board_ops(),
        }

    def handle(self, req: dict) -> dict:
        handler = self._ops.get(req.get("op", ""))
        if handler is None:
            return {"ok": False, "code": c.ERR_BAD_REQUEST,
                    "error": f"unknown op '{req.get('op')}'"}
        try:
            return {"ok": True, **handler(req)}
        except MeshError as exc:
            return {"ok": False, "code": exc.code, "error": str(exc)}
        except (KeyError, TypeError, ValueError) as exc:
            return {"ok": False, "code": c.ERR_BAD_REQUEST, "error": f"bad request: {exc}"}

    def _hello(self, req: dict) -> dict:
        return {"version": __version__, "sessions": self.registry.names()}

    def _join(self, req: dict) -> dict:
        info = self.registry.join(SessionInfo.from_dict(req["session"]))
        self.journal("join", info.to_dict())
        return {"session": info.to_dict(), "peers": self.registry.names()}

    def _leave(self, req: dict) -> dict:
        return {"left": self.registry.leave(req["name"])}

    def _send(self, req: dict) -> dict:
        msg = Message.from_dict(req["message"])
        if msg.kind not in c.KINDS:
            raise MeshError(f"unknown message kind '{msg.kind}'", c.ERR_BAD_REQUEST)
        self.gate.check(msg.sender)
        if msg.kind == c.KIND_REPLY:
            self.mailbox.put_reply(msg)
        elif not self.registry.known(msg.to):
            raise MeshError(
                f"no session named '{msg.to}' has joined the mesh "
                f"(joined: {self.registry.names() or 'nobody'})", c.ERR_UNKNOWN_PEER)
        else:
            self.mailbox.post(msg)
        self.journal("send", msg.to_dict())
        return {"id": msg.id, "queued": self.mailbox.depth(msg.to)}

    def _recv(self, req: dict) -> dict:
        name = req["name"]
        if not self.registry.known(name):  # self-heal after a hub restart: re-register
            self.registry.join(SessionInfo.from_dict(req.get("session") or {"name": name}))
        self.registry.touch(name, c.STATE_LISTENING)
        msg = self.mailbox.take(name, float(req.get("timeout", 0)))
        self.registry.touch(name, c.STATE_BUSY if msg else c.STATE_LISTENING)
        return {"message": msg.to_dict() if msg else None}

    def _await(self, req: dict) -> dict:
        msg = self.mailbox.await_reply(req["id"], float(req.get("timeout", 0)))
        return {"message": msg.to_dict() if msg else None}

    def _peers(self, req: dict) -> dict:
        return {"sessions": self.registry.rows()}

    def _stats(self, req: dict) -> dict:
        return {"version": __version__, "sessions": self.registry.rows(),
                **self.mailbox.stats()}

    def _shutdown(self, req: dict) -> dict:
        self.stop_event.set()
        return {"stopping": True}

    def undeliverable(self, response: dict) -> None:
        """Called by the server when a recv answer could not be written: requeue the message."""
        raw = response.get("message")
        if response.get("ok") and raw and raw.get("kind") != c.KIND_REPLY:
            self.mailbox.requeue_front(Message.from_dict(raw))
