# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""HubClient: the gatekeeper for every call to the hub.

All traffic goes through :meth:`HubClient.request`, which frames the request, applies the
socket timeout, acknowledges delivered messages, and backs off + retries when the hub's rate
gate says ``rate_limited`` (the overflow waits instead of crashing).
"""

from __future__ import annotations

import socket
import time
from collections.abc import Callable

from .constants import (
    ERR_RATE_LIMITED,
    OP_AWAIT,
    OP_BOARD_ADD,
    OP_BOARD_CLAIM,
    OP_BOARD_DONE,
    OP_HELLO,
    OP_JOIN,
    OP_RECV,
    OP_SEND,
)
from .errors import HubUnavailableError, MeshError
from .protocol import LineChannel

# Ops that agents run; only these may start a missing hub (status/down/peers never do).
AUTOSTART_OPS = (OP_JOIN, OP_RECV, OP_SEND, OP_AWAIT, OP_BOARD_ADD, OP_BOARD_CLAIM,
                 OP_BOARD_DONE)


class HubClient:
    """Stateless request/response client: one TCP connection per request."""

    def __init__(self, host: str, port: int, connect_timeout_s: float = 3.0,
                 margin_s: float = 5.0, max_retries: int = 3, retry_after_s: float = 2.0,
                 max_bytes: int = 1_048_576, sleep: Callable[[float], None] = time.sleep) -> None:
        self.host, self.port = host, port
        self.connect_timeout_s = connect_timeout_s
        self.margin_s = margin_s
        self.max_retries = max_retries
        self.retry_after_s = retry_after_s
        self.max_bytes = max_bytes
        self.sleep = sleep
        self.calls = 0
        self.retries = 0
        self.on_down: Callable[[], object] | None = None  # set by the SDK when autostart is on

    def request(self, payload: dict, wait_s: float = 0.0) -> dict:
        for attempt in range(self.max_retries + 1):
            resp = self._first(payload, wait_s) if attempt == 0 else self._once(payload, wait_s)
            if resp.get("ok"):
                return resp
            if resp.get("code") == ERR_RATE_LIMITED and attempt < self.max_retries:
                self.retries += 1
                self.sleep(self.retry_after_s * (attempt + 1))
                continue
            raise MeshError(resp.get("error", "the hub refused the request"), resp.get("code"))
        raise MeshError("unreachable")  # pragma: no cover - loop always returns or raises

    def _first(self, payload: dict, wait_s: float) -> dict:
        """First attempt: if the hub is down and this is an agent op, start it once, retry."""
        try:
            return self._once(payload, wait_s)
        except HubUnavailableError:
            if self.on_down is None or payload.get("op") not in AUTOSTART_OPS:
                raise
            self.on_down()
            return self._once(payload, wait_s)

    def is_up(self) -> bool:
        try:
            return bool(self._once({"op": OP_HELLO}, 0.0).get("ok"))
        except MeshError:
            return False

    def _once(self, payload: dict, wait_s: float) -> dict:
        self.calls += 1
        try:
            sock = socket.create_connection((self.host, self.port), self.connect_timeout_s)
        except OSError as exc:
            raise HubUnavailableError(
                f"The mesh hub is not running at {self.host}:{self.port}. "
                "Start it with `agymesh up` (or `agymesh hub` to watch it in a window)."
            ) from exc
        with sock:
            sock.settimeout(wait_s + self.margin_s)
            chan = LineChannel(sock, self.max_bytes)
            try:
                chan.send(payload)
                resp = chan.recv()
                if resp is None:
                    raise HubUnavailableError("the hub closed the connection without answering")
                if payload.get("op") == OP_RECV and resp.get("ok") and resp.get("message"):
                    chan.send({"ack": True})
            except TimeoutError as exc:
                raise MeshError(f"the hub did not answer within {wait_s + self.margin_s}s") from exc
            return resp
