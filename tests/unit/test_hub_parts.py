# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""MailboxStore, SessionRegistry and RateGate with an injected clock."""

from __future__ import annotations

import pytest

from agymesh.errors import MeshError
from agymesh.hub.gate import RateGate
from agymesh.hub.mailbox import MailboxStore
from agymesh.hub.registry import SessionRegistry
from agymesh.models import Message, SessionInfo


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


class TestMailboxStore:
    def test_fifo_and_timeout(self):
        box = MailboxStore(10, 60, "reject_oldest")
        box.post(Message("m", "poem", "1"))
        box.post(Message("m", "poem", "2"))
        assert [box.take("poem", 0).content, box.take("poem", 0).content] == ["1", "2"]
        assert box.take("poem", 0.05) is None

    def test_reject_oldest_drops_head(self):
        box = MailboxStore(1, 60, "reject_oldest")
        box.post(Message("m", "a", "old"))
        box.post(Message("m", "a", "new"))
        assert box.take("a", 0).content == "new"
        assert box.stats()["dropped"] == 1

    def test_reject_newest_raises_backpressure(self):
        box = MailboxStore(1, 60, "reject_newest")
        box.post(Message("m", "a", "x"))
        with pytest.raises(MeshError, match="full"):
            box.post(Message("m", "a", "y"))

    def test_expired_messages_are_skipped(self):
        clock = Clock()
        box = MailboxStore(5, 10, "reject_oldest", clock=clock)
        box.post(Message("m", "a", "stale", created=clock.now - 60))
        assert box.take("a", 0) is None

    def test_requeue_front_and_reply_book(self):
        box = MailboxStore(5, 60, "reject_oldest")
        box.post(Message("m", "a", "second"))
        box.requeue_front(Message("m", "a", "first"))
        assert box.take("a", 0).content == "first"
        assert box.depth("a") == 1
        box.put_reply(Message("a", "m", "ans", kind="reply", reply_to="r1"))
        assert box.await_reply("r1", 0).content == "ans"
        assert box.await_reply("r2", 0.05) is None


class TestSessionRegistry:
    def test_join_touch_rows_stale_leave(self):
        clock = Clock()
        reg = SessionRegistry(stale_after_s=30, clock=clock)
        reg.join(SessionInfo("poem", agy_pid=7))
        reg.touch("poem", "listening")
        reg.touch("ghost", "busy")
        assert reg.known("poem") and reg.names() == ["poem"]
        assert reg.rows()[0]["state"] == "listening"
        clock.now += 31
        assert reg.rows()[0]["state"] == "stale"
        assert reg.leave("poem") and not reg.leave("poem")


class TestRateGate:
    def test_burst_then_limit_then_refill(self):
        clock = Clock()
        gate = RateGate(60, 2, 1, clock=clock)
        gate.check("a")
        gate.check("a")
        with pytest.raises(MeshError, match="too fast"):
            gate.check("a")
        gate.check("b")
        clock.now += 1.0
        gate.check("a")

    def test_from_config_defaults(self):
        gate = RateGate.from_config({})
        assert gate.burst == 30 and gate.retry_after_s == 2
