# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""Hub auto-start race: many agents find NO hub at the same instant and all try to start one.

Real processes: every launcher may spawn ``python -m agymesh hub``. Exactly one may survive
(the exclusive port bind), and every agent must end up joined to it.
"""

from __future__ import annotations

import json
import socket
import subprocess
import threading
import time

import pytest

from agymesh import sdk_base
from agymesh.config import MeshConfig
from agymesh.launcher import HubLauncher
from agymesh.sdk import AgyMesh
from tests.conftest import FakeGuard, config_data

pytestmark = pytest.mark.slow
AGENTS = ["art", "poem", "joke", "extra"]


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def race_env(tmp_path, monkeypatch):
    port = free_port()
    cdir = tmp_path / "config"
    cdir.mkdir()
    data = config_data(tmp_path, port)
    data["hub"]["start_wait_s"] = 30
    rates = {"rate_limits": data.pop("rate_limits")}
    (cdir / "setup.json").write_text(json.dumps(data), encoding="utf-8")
    (cdir / "rate_limits.json").write_text(json.dumps(rates), encoding="utf-8")
    spawned: list[subprocess.Popen] = []
    lock = threading.Lock()

    def recording_spawn(*args, **kwargs):
        proc = subprocess.Popen(*args, **kwargs)
        with lock:
            spawned.append(proc)
        return proc

    def launcher(client, config_dir, *args, **kwargs):
        return HubLauncher(client, config_dir, *args, spawn=recording_spawn, **kwargs)

    monkeypatch.setattr(sdk_base, "HubLauncher", launcher)
    yield cdir, spawned
    for proc in spawned:
        if proc.poll() is None:
            proc.kill()


@pytest.mark.parametrize("jitter", [0.0, 1.5])
def test_simultaneous_agents_start_exactly_one_hub(race_env, jitter):
    cdir, spawned = race_env
    meshes = []
    for i, _ in enumerate(AGENTS):
        cfg = MeshConfig.load(cdir)
        cfg.data["hub"]["autostart_jitter_s"] = jitter
        meshes.append(AgyMesh(cfg, guard=FakeGuard(5000 + i)))
    barrier = threading.Barrier(len(AGENTS))
    errors: list[Exception] = []

    def agent(mesh, name):
        barrier.wait()
        try:
            mesh.join(name)
        except Exception as exc:  # noqa: BLE001 - surfaced by the assert below
            errors.append(exc)

    threads = [threading.Thread(target=agent, args=(m, n)) for m, n in zip(meshes, AGENTS, strict=True)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(60)
    assert errors == []
    assert sorted(r["name"] for r in meshes[0].peers()) == sorted(AGENTS)
    time.sleep(1.0)  # losers exit right after their failed bind
    alive = [p for p in spawned if p.poll() is None]
    print(f"jitter={jitter}s: hub processes spawned={len(spawned)}, survived={len(alive)}")
    assert len(spawned) >= 1 and len(alive) == 1
    assert meshes[0].hub_down() is True


def test_admin_ops_never_autostart(race_env):
    cdir, spawned = race_env
    mesh = AgyMesh(MeshConfig.load(cdir), guard=FakeGuard())
    with pytest.raises(Exception, match="not running"):
        mesh.status()
    assert spawned == []
