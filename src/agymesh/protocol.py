# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""LineChannel: newline-delimited JSON framing over a stream socket.

The failed version called ``recv(4096)`` once and assumed it got exactly one whole message.
TCP is a byte stream: two messages can arrive glued together, or one message in two pieces.
This channel buffers until a full ``\\n``-terminated frame is present and caps the frame size.
"""

from __future__ import annotations

import json
import socket

from .errors import ProtocolError

CHUNK = 65536


class LineChannel:
    """One JSON object per line, UTF-8, never more than ``max_bytes`` per frame."""

    def __init__(self, sock: socket.socket, max_bytes: int = 1_048_576) -> None:
        self.sock = sock
        self.max_bytes = max_bytes
        self._buf = b""

    def send(self, obj: dict) -> None:
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8") + b"\n"
        if len(data) > self.max_bytes:
            raise ProtocolError(f"message is {len(data)} bytes; the limit is {self.max_bytes}")
        self.sock.sendall(data)

    def recv(self) -> dict | None:
        """Return the next frame, or None when the peer closed the connection."""
        while b"\n" not in self._buf:
            if len(self._buf) > self.max_bytes:
                raise ProtocolError(f"incoming frame exceeds {self.max_bytes} bytes")
            chunk = self.sock.recv(CHUNK)
            if not chunk:
                return None
            self._buf += chunk
        line, self._buf = self._buf.split(b"\n", 1)
        try:
            obj = json.loads(line.decode("utf-8"))
        except ValueError as exc:
            raise ProtocolError(f"frame is not valid JSON: {exc}") from exc
        if not isinstance(obj, dict):
            raise ProtocolError("frame must be a JSON object")
        return obj
