# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""HubRouter (pure logic), LineChannel framing and the journal."""

from __future__ import annotations

import json
import socket

import pytest

from agymesh.errors import ProtocolError
from agymesh.hub.gate import RateGate
from agymesh.hub.mailbox import MailboxStore
from agymesh.hub.registry import SessionRegistry
from agymesh.hub.router import HubRouter
from agymesh.hub.server import Journal
from agymesh.models import Message
from agymesh.protocol import LineChannel
from agymesh.version import __version__


@pytest.fixture
def router():
    return HubRouter(MailboxStore(10, 60, "reject_oldest"), SessionRegistry(60), RateGate(600, 50, 1))


def send(router, msg: Message) -> dict:
    return router.handle({"op": "send", "message": msg.to_dict()})


class TestHubRouter:
    def test_join_send_recv_reply_await(self, router):
        assert router.handle({"op": "join", "session": {"name": "poem"}})["peers"] == ["poem"]
        req = Message("master", "poem", "write")
        assert send(router, req)["ok"]
        got = router.handle({"op": "recv", "name": "poem", "timeout": 0})["message"]
        assert got["id"] == req.id
        assert send(router, Message("poem", "", "done", kind="reply", reply_to=req.id))["ok"]
        assert router.handle({"op": "await", "id": req.id, "timeout": 0})["message"]["content"] == "done"

    def test_unknown_peer_and_bad_requests(self, router):
        resp = send(router, Message("master", "ghost", "x"))
        assert resp == {"ok": False, "code": "unknown_peer", "error": resp["error"]}
        assert router.handle({"op": "nope"})["code"] == "bad_request"
        assert router.handle({"op": "send"})["code"] == "bad_request"
        router.handle({"op": "join", "session": {"name": "a"}})
        assert send(router, Message("m", "a", "x", kind="weird"))["code"] == "bad_request"

    def test_recv_self_registers_after_hub_restart(self, router):
        router.handle({"op": "recv", "name": "joke", "timeout": 0, "session": {"name": "joke"}})
        assert router.handle({"op": "peers"})["sessions"][0]["name"] == "joke"

    def test_hello_stats_leave_shutdown(self, router):
        assert router.handle({"op": "hello"})["version"] == __version__
        assert "queued" in router.handle({"op": "stats"})
        assert router.handle({"op": "leave", "name": "x"})["left"] is False
        router.handle({"op": "shutdown"})
        assert router.stop_event.is_set()

    def test_undeliverable_message_is_requeued(self, router):
        router.handle({"op": "join", "session": {"name": "a"}})
        msg = Message("m", "a", "lost?")
        router.undeliverable({"ok": True, "message": msg.to_dict()})
        assert router.mailbox.take("a", 0).id == msg.id


class TestLineChannel:
    def test_glued_and_split_frames(self):
        a, b = socket.socketpair()
        with a, b:
            a.sendall(b'{"n": 1}\n{"n"')
            a.sendall(b': 2}\n')
            chan = LineChannel(b)
            assert [chan.recv(), chan.recv()] == [{"n": 1}, {"n": 2}]
            a.close()
            assert chan.recv() is None

    def test_limits_and_garbage(self):
        a, b = socket.socketpair()
        with a, b:
            with pytest.raises(ProtocolError):
                LineChannel(a, max_bytes=10).send({"text": "x" * 50})
            a.sendall(b"not json\n[1]\n" + b"y" * 40)
            chan = LineChannel(b, max_bytes=20)
            with pytest.raises(ProtocolError, match="valid JSON"):
                chan.recv()
            with pytest.raises(ProtocolError, match="JSON object"):
                chan.recv()
            with pytest.raises(ProtocolError, match="exceeds"):
                chan.recv()


def test_journal_appends_json_lines(tmp_path):
    path = tmp_path / "j" / "log.jsonl"
    Journal(path)("send", {"id": "x"})
    Journal(None)("send", {"id": "y"})
    assert json.loads(path.read_text(encoding="utf-8"))["id"] == "x"
