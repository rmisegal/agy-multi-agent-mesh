# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""AdminMixin: foreground hub, launch (terminal spawn mocked) and hub_up with a running hub."""

from __future__ import annotations

import threading

import pytest

from agymesh import sdk_admin
from agymesh.config import MeshConfig
from agymesh.sdk import AgyMesh
from tests.conftest import config_data

pytestmark = pytest.mark.slow


class RecordingLauncher:
    opened: list = []

    def __init__(self, *args, **kwargs) -> None:
        pass

    def open(self, spec, boot):
        RecordingLauncher.opened.append((spec.name, boot))
        return [boot]


def test_launch_opens_workers_and_master_with_boot_prompts(tmp_path, monkeypatch):
    monkeypatch.setattr(sdk_admin, "TerminalLauncher", RecordingLauncher)
    RecordingLauncher.opened = []
    mesh = AgyMesh(MeshConfig(config_data(tmp_path), tmp_path))
    assert mesh.launch(["poem"], with_master=True) == ["poem", "master"]
    assert "agent 'poem'" in RecordingLauncher.opened[0][1]
    assert "master 'master'" in RecordingLauncher.opened[1][1]
    assert mesh.launch() == ["art", "poem", "joke"]


def test_foreground_hub_serves_until_down(tmp_path):
    mesh = AgyMesh(MeshConfig(config_data(tmp_path), tmp_path))
    ready = threading.Event()
    port = {}

    def on_ready(host, bound):
        port["p"] = bound
        ready.set()

    t = threading.Thread(target=mesh.serve_hub, kwargs={"port": 0, "on_ready": on_ready},
                         daemon=True)
    t.start()
    assert ready.wait(5)
    client_mesh = AgyMesh(MeshConfig(config_data(tmp_path, port["p"]), tmp_path))
    assert client_mesh.hub_up() is False
    assert client_mesh.hub_down() is True
    t.join(5)
    assert not t.is_alive()
    assert client_mesh.hub_down() is False
