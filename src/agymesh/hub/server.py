# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""HubServer: localhost TCP front-end of the router. One request per connection.

Lessons applied: the accept loop uses a timeout so Ctrl+C and ``agymesh down`` stop it at once;
the port is bound EXCLUSIVELY (on Windows, SO_REUSEADDR lets two hubs share a port, which made
the old "jitter" start-up race possible) - the bind itself is the single-instance lock.
"""

from __future__ import annotations

import json
import socket
import sys
import threading
import time
from pathlib import Path

from ..constants import OP_RECV
from ..errors import HubUnavailableError, ProtocolError
from ..protocol import LineChannel
from .router import HubRouter


class Journal:
    """Append-only JSON-lines log of joins and messages (for debugging and teaching)."""

    def __init__(self, path: Path | None) -> None:
        self.path = Path(path) if path else None
        self._lock = threading.Lock()
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def __call__(self, event: str, data: dict) -> None:
        if not self.path:
            return
        line = json.dumps({"t": time.time(), "event": event, **data}, ensure_ascii=False)
        with self._lock, self.path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def exclusive_socket() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if sys.platform == "win32":
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)  # type: ignore[attr-defined]
    else:  # pragma: no cover - POSIX semantics: REUSEADDR does not allow a double bind
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock


class HubServer:
    """Accept loop + one worker thread per connection."""

    def __init__(self, router: HubRouter, host: str, port: int,
                 accept_timeout_s: float = 1.0, max_bytes: int = 1_048_576,
                 ack_timeout_s: float = 5.0) -> None:
        self.router = router
        self.host, self.port = host, port
        self.accept_timeout_s = accept_timeout_s
        self.ack_timeout_s = ack_timeout_s
        self.max_bytes = max_bytes
        self.sock: socket.socket | None = None

    def bind(self) -> int:
        sock = exclusive_socket()
        try:
            sock.bind((self.host, self.port))
        except OSError as exc:
            sock.close()
            raise HubUnavailableError(f"port {self.host}:{self.port} is already taken ({exc})") from exc
        sock.listen(64)
        sock.settimeout(self.accept_timeout_s)
        self.sock = sock
        self.port = sock.getsockname()[1]
        return self.port

    def serve_forever(self) -> None:
        if self.sock is None:
            self.bind()
        try:
            while not self.router.stop_event.is_set():
                try:
                    conn, _ = self.sock.accept()  # type: ignore[union-attr]
                except TimeoutError:
                    continue
                threading.Thread(target=self._serve_conn, args=(conn,), daemon=True).start()
        finally:
            self.sock.close()  # type: ignore[union-attr]

    def stop(self) -> None:
        self.router.stop_event.set()

    def _serve_conn(self, conn: socket.socket) -> None:
        conn.settimeout(None)
        chan = LineChannel(conn, self.max_bytes)
        try:
            req = chan.recv()
            if req is None:
                return
            resp = self.router.handle(req)
            try:
                chan.send(resp)
                if req.get("op") == OP_RECV and resp.get("message"):
                    self._expect_ack(conn, chan)
            except (OSError, ProtocolError):
                self.router.undeliverable(resp)
        except (ProtocolError, OSError):
            pass
        finally:
            conn.close()

    def _expect_ack(self, conn: socket.socket, chan: LineChannel) -> None:
        """A delivered message counts only after the client confirms it; else it is requeued."""
        conn.settimeout(self.ack_timeout_s)
        ack = chan.recv()
        if not ack or not ack.get("ack"):
            raise ProtocolError("message was not acknowledged by the receiving session")
