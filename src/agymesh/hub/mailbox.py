# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""MailboxStore: one FIFO queue per agent plus a reply book keyed by request id.

Messages wait in the hub until the target session asks for them (``recv``), so nothing is lost
while an agy session is busy thinking. That replaces the failed daemon + inbox.ipc bridge, which
held a single file and overwrote it when a second message arrived.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from collections.abc import Callable

from ..constants import ERR_MAILBOX_FULL, OVERFLOW_REJECT_NEWEST
from ..errors import MeshError
from ..models import Message


class MailboxStore:
    """Thread-safe queues with max depth, overflow strategy and message time-to-live."""

    def __init__(self, max_depth: int, ttl_s: float, overflow: str,
                 clock: Callable[[], float] = time.time) -> None:
        self.max_depth = max_depth
        self.ttl_s = ttl_s
        self.overflow = overflow
        self.clock = clock
        self.dropped = 0
        self._boxes: dict[str, deque[Message]] = {}
        self._replies: dict[str, Message] = {}
        self._cond = threading.Condition()

    def post(self, msg: Message) -> None:
        with self._cond:
            box = self._boxes.setdefault(msg.to, deque())
            if len(box) >= self.max_depth:
                if self.overflow == OVERFLOW_REJECT_NEWEST:
                    raise MeshError(
                        f"mailbox of '{msg.to}' is full ({self.max_depth} messages waiting)",
                        ERR_MAILBOX_FULL,
                    )
                box.popleft()
                self.dropped += 1
            box.append(msg)
            self._cond.notify_all()

    def requeue_front(self, msg: Message) -> None:
        """Put back a message whose delivery failed (e.g. the agy tool call was killed)."""
        with self._cond:
            self._boxes.setdefault(msg.to, deque()).appendleft(msg)
            self._cond.notify_all()

    def take(self, name: str, timeout: float) -> Message | None:
        deadline = self.clock() + max(0.0, timeout)
        with self._cond:
            while True:
                msg = self._pop_fresh(name)
                if msg is not None:
                    return msg
                left = deadline - self.clock()
                if left <= 0:
                    return None
                self._cond.wait(min(left, 1.0))

    def _pop_fresh(self, name: str) -> Message | None:
        box = self._boxes.get(name)
        while box:
            msg = box.popleft()
            if msg.age(self.clock()) <= self.ttl_s:
                return msg
            self.dropped += 1
        return None

    def put_reply(self, msg: Message) -> None:
        with self._cond:
            self._replies[str(msg.reply_to)] = msg
            self._cond.notify_all()

    def await_reply(self, request_id: str, timeout: float) -> Message | None:
        deadline = self.clock() + max(0.0, timeout)
        with self._cond:
            while request_id not in self._replies:
                left = deadline - self.clock()
                if left <= 0:
                    return None
                self._cond.wait(min(left, 1.0))
            return self._replies.pop(request_id)

    def depth(self, name: str) -> int:
        with self._cond:
            return len(self._boxes.get(name, ()))

    def stats(self) -> dict:
        with self._cond:
            return {"queued": {k: len(v) for k, v in self._boxes.items() if v},
                    "replies_waiting": len(self._replies), "dropped": self.dropped}
