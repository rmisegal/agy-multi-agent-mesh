# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""End-to-end: three simulated agy sessions (art, poem, joke) follow the AGY.md protocol.

Each worker thread does exactly what the generated AGY.md tells a real agy session to do:
join, then loop on ``wait``; PING -> reply PONG; meshcheck -> ping-all --reply-to; task -> reply.
"""

from __future__ import annotations

import threading

import pytest

from agymesh.constants import KIND_MESHCHECK, KIND_PING
from agymesh.errors import MeshError

pytestmark = pytest.mark.slow
WORKERS = {"art": 1001, "poem": 1002, "joke": 1003}


def worker_loop(mesh, name: str, stop: threading.Event) -> None:
    mesh.join(name)
    while not stop.is_set():
        msg = mesh.wait(name, timeout_s=0.3)
        if msg is None:
            continue
        if msg.kind == KIND_PING:
            mesh.reply(name, msg.id, text=f"PONG {name}")
        elif msg.kind == KIND_MESHCHECK:
            mesh.relay_pings(name, msg.id)
        else:
            mesh.reply(name, msg.id, text=f"[{name}] {msg.content}")


@pytest.fixture
def trio(mesh_factory):
    stop = threading.Event()
    threads = []
    for name, pid in WORKERS.items():
        t = threading.Thread(target=worker_loop, args=(mesh_factory(pid), name, stop), daemon=True)
        t.start()
        threads.append(t)
    master = mesh_factory(9000)
    for _ in range(50):
        if len(master.peers()) == len(WORKERS):
            break
        threading.Event().wait(0.05)
    yield master
    stop.set()
    for t in threads:
        t.join(timeout=3)


def test_peers_lists_every_joined_session_with_its_agy_pid(trio):
    rows = {r["name"]: r for r in trio.peers()}
    assert set(rows) == set(WORKERS)
    assert {n: r["agy_pid"] for n, r in rows.items()} == WORKERS


def test_ping_all_gets_pong_from_each_agy_session(trio):
    results = trio.ping_all("master")
    assert {p: r.text for p, r in results.items()} == {n: f"PONG {n}" for n in WORKERS}
    assert {p: r.answered_by for p, r in results.items()} == {
        n: f"agy pid {pid}" for n, pid in WORKERS.items()}


def test_dispatch_all_uses_each_agents_template_and_gathers_all(trio):
    results = trio.dispatch_all("Israeli winter", "master", timeout_s=10)
    assert all(r.ok for r in results.values())
    assert results["art"].text.startswith("[art] Create expressive ASCII art")
    assert "Israeli winter" in results["poem"].text
    assert results["joke"].text.startswith("[joke] ")


def test_custom_dispatch_reaches_only_named_peers(trio):
    results = trio.dispatch({"poem": "rain", "joke": "puddles"}, "master", timeout_s=10)
    assert {p: r.text for p, r in results.items()} == {"poem": "[poem] rain",
                                                        "joke": "[joke] puddles"}


def test_mesh_check_is_a_full_mesh(trio):
    report = trio.mesh_check("master")
    assert report.broken == []
    assert report.total == 4 * 3


def test_unknown_peer_fails_fast_instead_of_hanging(trio):
    results = trio.dispatch({"ghost": "hello"}, "master", timeout_s=5)
    assert not results["ghost"].ok
    assert "no session named 'ghost'" in results["ghost"].error


def test_send_from_plain_terminal_is_refused(mesh_factory, tmp_path):
    from agymesh.config import MeshConfig
    from agymesh.procs import OriginGuard, ProcessTable
    from agymesh.sdk import AgyMesh

    mesh = mesh_factory()
    real = AgyMesh(MeshConfig(mesh.config.data, tmp_path),
                   guard=OriginGuard(["agy.exe", "agy"], True, ProcessTable))
    with pytest.raises(MeshError, match="must be run BY an agy session"):
        real.send("poem", "hi", "master")
