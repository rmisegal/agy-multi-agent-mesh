# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""HubClient gatekeeper against the live hub, plus failure paths."""

from __future__ import annotations

import socket
import threading

import pytest

from agymesh.client import HubClient
from agymesh.errors import HubUnavailableError, MeshError
from agymesh.hub.server import HubServer
from agymesh.version import __version__

pytestmark = pytest.mark.slow


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TestHubClient:
    def test_hello_and_is_up(self, live_hub):
        _, port = live_hub
        client = HubClient("127.0.0.1", port)
        assert client.is_up()
        assert client.request({"op": "hello"})["version"] == __version__

    def test_down_hub_explains_how_to_start_it(self):
        client = HubClient("127.0.0.1", free_port(), connect_timeout_s=0.5)
        assert not client.is_up()
        with pytest.raises(HubUnavailableError, match="agymesh up"):
            client.request({"op": "hello"})

    def test_agent_ops_call_on_down_once_admin_ops_never(self):
        client = HubClient("127.0.0.1", free_port(), connect_timeout_s=0.5)
        calls = []
        client.on_down = lambda: calls.append(1)
        with pytest.raises(HubUnavailableError):
            client.request({"op": "join", "session": {"name": "a"}})
        assert calls == [1]
        with pytest.raises(HubUnavailableError):
            client.request({"op": "stats"})
        assert calls == [1]

    def test_on_down_that_starts_the_hub_makes_the_retry_succeed(self, tmp_path):
        from agymesh.config import MeshConfig
        from agymesh.sdk import AgyMesh
        from tests.conftest import config_data

        mesh = AgyMesh(MeshConfig(config_data(tmp_path), tmp_path))
        server = mesh.build_server(port=0)
        client = HubClient("127.0.0.1", server.bind(), connect_timeout_s=0.5)
        server.sock.close()  # the port is now free: the hub is "down"
        holder = {}

        def start():
            holder["s"] = mesh.build_server(port=client.port)
            holder["s"].bind()
            threading.Thread(target=holder["s"].serve_forever, daemon=True).start()

        client.on_down = start
        assert client.request({"op": "join", "session": {"name": "a"}})["peers"] == ["a"]
        holder["s"].stop()

    def test_hub_error_is_raised_with_code(self, live_hub):
        _, port = live_hub
        with pytest.raises(MeshError) as info:
            HubClient("127.0.0.1", port).request({"op": "bogus"})
        assert info.value.code == "bad_request"

    def test_rate_limited_requests_back_off_and_retry(self, live_hub):
        server, port = live_hub
        server.router.gate.burst = 1
        server.router.gate.rate = 1000.0
        server.router.handle({"op": "join", "session": {"name": "a"}})
        naps = []
        client = HubClient("127.0.0.1", port, retry_after_s=0.01, sleep=naps.append)
        msg = {"sender": "m", "to": "a", "content": "x"}
        for _ in range(3):
            client.request({"op": "send", "message": msg})
        assert client.retries == len(naps)

    def test_slow_hub_answer_times_out(self, live_hub):
        _, port = live_hub
        client = HubClient("127.0.0.1", port, margin_s=0.2)
        with pytest.raises(MeshError, match="did not answer"):
            client.request({"op": "await", "id": "never", "timeout": 2}, wait_s=0)


class TestHubServer:
    def test_second_hub_cannot_bind_same_port(self, live_hub):
        server, port = live_hub
        with pytest.raises(HubUnavailableError, match="already taken"):
            HubServer(server.router, "127.0.0.1", port).bind()

    def test_unacknowledged_message_goes_back_to_the_queue(self, live_hub):
        server, port = live_hub
        server.ack_timeout_s = 0.2
        server.router.handle({"op": "join", "session": {"name": "a"}})
        server.router.handle({"op": "send", "message": {"sender": "m", "to": "a",
                                                        "content": "keep me"}})
        with socket.create_connection(("127.0.0.1", port)) as sock:
            sock.sendall(b'{"op": "recv", "name": "a", "timeout": 0}\n')
            assert b"keep me" in sock.recv(65536)
        for _ in range(40):
            if server.router.mailbox.depth("a"):
                break
            threading.Event().wait(0.05)
        assert server.router.mailbox.take("a", 0).content == "keep me"

    def test_empty_connection_is_ignored(self, live_hub):
        _, port = live_hub
        socket.create_connection(("127.0.0.1", port)).close()
        assert HubClient("127.0.0.1", port).is_up()
