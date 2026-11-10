# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""Shared fixtures: a config built from the real config files, a live hub, fake agy origins."""

from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest

from agymesh.config import MeshConfig, read_json
from agymesh.sdk import AgyMesh

ROOT = Path(__file__).resolve().parents[1]
REAL_TEAM = ROOT / "examples" / "creative-trio" / "team.json"


class FakeGuard:
    """Pretends the command runs inside the agy process ``agy_pid`` (or a plain terminal)."""

    def __init__(self, agy_pid: int | None = 4242) -> None:
        self.agy_pid = agy_pid

    def stamp(self) -> dict:
        return {"agy_pid": self.agy_pid, "external": self.agy_pid is None}


def config_data(tmp_path: Path, port: int = 0) -> dict:
    data = read_json(ROOT / "config" / "setup.json")
    data["rate_limits"] = read_json(ROOT / "config" / "rate_limits.json")["rate_limits"]
    data["hub"]["port"] = port
    data["hub"]["journal"] = str(tmp_path / "journal.jsonl")
    data["hub"]["accept_timeout_s"] = 0.1
    data["team_file"] = str(team_copy(tmp_path))
    data["orchestrator"]["results_dir"] = str(tmp_path / "results")
    data["orchestrator"]["open_result"] = False
    return data


def team_copy(tmp_path: Path) -> Path:
    """The creative-trio team, with its agent folders inside tmp_path."""
    target = tmp_path / "team" / "team.json"
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(REAL_TEAM.read_text(encoding="utf-8"), encoding="utf-8")
    return target


@pytest.fixture
def cfg(tmp_path) -> MeshConfig:
    return MeshConfig(config_data(tmp_path), tmp_path)


@pytest.fixture
def config_dir(tmp_path) -> Path:
    cdir = tmp_path / "config"
    cdir.mkdir()
    data = config_data(tmp_path)
    rates = {"rate_limits": data.pop("rate_limits")}
    (cdir / "setup.json").write_text(json.dumps(data), encoding="utf-8")
    (cdir / "rate_limits.json").write_text(json.dumps(rates), encoding="utf-8")
    return cdir


@pytest.fixture
def live_hub(tmp_path):
    """A real hub on a free localhost port, served from a background thread."""
    mesh = AgyMesh(MeshConfig(config_data(tmp_path), tmp_path))
    server = mesh.build_server(port=0)
    port = server.bind()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server, port
    server.stop()
    thread.join(timeout=3)


@pytest.fixture
def mesh_factory(tmp_path, live_hub):
    """Build an AgyMesh client for a given fake agy pid, connected to the live hub."""
    _, port = live_hub

    def make(agy_pid: int | None = 4242) -> AgyMesh:
        return AgyMesh(MeshConfig(config_data(tmp_path, port), tmp_path), guard=FakeGuard(agy_pid))

    return make
